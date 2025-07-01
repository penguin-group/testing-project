from odoo import fields, models, api, _
import pandas as pd
from io import BytesIO
import base64
from datetime import datetime, timedelta
import pytz

from odoo.exceptions import UserError


def to_naive_utc(local_dt):
    """Takes a naive Timestamp in local time, makes it a naive Timestamp in UTC and then
     converts it to Python's native datetime object."""
    local_tz = pytz.timezone("America/Asuncion")
    aware_local = local_tz.localize(local_dt)
    aware_utc = aware_local.astimezone(pytz.UTC)
    return aware_utc.replace(tzinfo=None).to_pydatetime()


class ImportAttendanceRecords(models.TransientModel):
    _name = 'import.attendance.records.wizard'
    _description = 'Import Attendance Records'

    csv_file = fields.Binary(string='CSV File')

    def import_attendance_records(self):
        """
        Reads a CSV file, cleans and restructure its data, and upload to Odoo's hr.attendance table.
        """
        self.ensure_one()

        try:
            csv_data = base64.b64decode(self.csv_file)
            df = pd.read_csv(BytesIO(csv_data), encoding='latin1', skiprows=5, sep=';')
            df = df.loc[:, df.columns.str.strip().astype(bool) & ~df.columns.str.contains('^Unnamed')]
            df = df[['ID', 'Fecha', 'Hora de registro de entrada', 'Salida a', 'Nombre']]
            df = df[  # 2.1. If there is no check-in or check-out (e.g. '-'), or there is no Cedula, ignore the whole row
                (df['ID'].notna()) &
                (df['ID'] != '-') &
                (df['Hora de registro de entrada'].notna()) &
                (df['Salida a'].notna()) &
                (df['Hora de registro de entrada'] != '-') &
                (df['Salida a'] != '-')
                ].copy()

            df.columns = df.columns.str.strip()

            # convert 'Fecha' to date object and 'Hora de registro de entrada' to time
            df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')
            df['Hora de registro de entrada'] = pd.to_datetime(df['Hora de registro de entrada'], format='%H:%M').dt.time
            df['Salida a'] = pd.to_datetime(df['Salida a'], format='%H:%M').dt.time

            # Compute checkin_datetime
            df['checkin_datetime'] = df['Fecha'].astype(str) + ' ' + df['Hora de registro de entrada'].astype(str)
            df['checkin_datetime'] = pd.to_datetime(df['checkin_datetime'])

            # Compute checkout_datetime
            checkout_dt = []
            for i, row in df.iterrows():
                if row['Salida a'] < row['Hora de registro de entrada']:
                    checkout = datetime.combine(
                        row['Fecha'].date() + timedelta(days=1),
                        row['Salida a']
                    )
                else:
                    checkout = datetime.combine(
                        row['Fecha'].date(),
                        row['Salida a']
                    )
                checkout_dt.append(checkout)
            df['checkout_datetime'] = checkout_dt

            df['total_time_logged'] = df['checkout_datetime'] - df['checkin_datetime']  # compute total_time_logged
            threshold = pd.Timedelta(minutes=30)
            df = df[df['total_time_logged'] > threshold].copy()  # remove row if time logged is less than 30 min
            df.reset_index(drop=True, inplace=True)

            # employee_identification --> cedula
            employee_identification = df['ID'].apply(lambda x: str(int(x)).strip()).unique().tolist()

            # Fetch all matching employees once
            employees = self.env['hr.employee'].search([('identification_id', 'in', employee_identification)])
            emp_map = {e.identification_id: e.id for e in employees}

            # Filter rows without matching employees
            df['employee_id'] = df['ID'].apply(lambda x: emp_map.get(str(int(x)).strip()))
            df = df[df['employee_id'].notna()]

            # Prepare attendance keys for bulk check
            keys = []
            for _, row in df.iterrows():
                key = (int(row['employee_id']), row['checkin_datetime'].replace(tzinfo=None))
                keys.append(key)

            # Search existing attendances
            domain = [
                ('employee_id', 'in', list(set([k[0] for k in keys]))),
                ('check_in', 'in', list(set([k[1] for k in keys])))
            ]
            existing_attendance = self.env['hr.attendance'].search(domain)
            existing_keys = set(
                (att.employee_id.id, att.check_in.replace(tzinfo=None))
                for att in existing_attendance
            )

            # create attendances
            new_attendances = []
            for _, row in df.iterrows():
                key = (int(row['employee_id']), row['checkin_datetime'].replace(tzinfo=None))
                if key in existing_keys:
                    continue

                new_attendances.append({
                    'employee_id': int(row['employee_id']),
                    'check_in': to_naive_utc(row['checkin_datetime']),
                    'check_out': to_naive_utc(row['checkout_datetime']) if row['checkout_datetime'] else False,
                })

            if new_attendances:
                self.env['hr.attendance'].create(new_attendances)
            return {'type': 'ir.actions.act_window_close'}

        except Exception as e:
            raise UserError(e)
