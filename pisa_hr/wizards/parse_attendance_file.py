from odoo import fields, models, api, _
import pandas as pd
from io import BytesIO
import base64
from datetime import datetime, timedelta

from odoo.exceptions import UserError


class ParseAttendanceFile(models.TransientModel):
    _name = 'parse.attendance.file.wizard'
    _description = 'Parse Attendance File'

    csv_file = fields.Binary(string='CSV File')

    processed_csv_file = fields.Binary(string='Processed CSV File', readonly=True)
    processed_csv_file_name = fields.Char(string='Processed File Name')

    def parse_csv(self):
        """
        Reads a CSV file, cleans and restructure its data, and generates a new CSV file from it.
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
            employee_id_mapping = {e.identification_id: e.id for e in employees}
            employee_name_mapping = {e.identification_id: e.name for e in employees}

            # Filter rows without matching employees
            df['employee_id'] = df['ID'].apply(lambda x: employee_id_mapping.get(str(int(x)).strip()))
            df = df[df['employee_id'].notna()]

            df['Nombre'] = df['ID'].apply(lambda x: employee_name_mapping.get(str(int(x)).strip()))

            # Group attendances that will be written to the new CSV
            new_attendances = []
            for _, row in df.iterrows():
                new_attendances.append({
                    'employee_name': row['Nombre'],
                    'check_in': row['checkin_datetime'].to_pydatetime(),
                    'check_out': row['checkout_datetime'].to_pydatetime() if row['checkout_datetime'] else False,
                })

            new_attendances_df = pd.DataFrame.from_dict(new_attendances)

            output = BytesIO()
            new_attendances_df.to_csv(output, index=False, sep=",", encoding='utf-8')
            file_bytes = output.getvalue()
            output.close()

            # Encode as base64
            file_data_b64 = base64.b64encode(file_bytes)

            # Save into transient model fields
            self.processed_csv_file = file_data_b64
            self.processed_csv_file_name = 'imported_attendances.csv'

            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/parse.attendance.file.wizard/{self.id}/processed_csv_file/{self.processed_csv_file_name}?download=true',
                'close': True
            }

        except Exception as e:
            raise UserError(e)
