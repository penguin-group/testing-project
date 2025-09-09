from odoo import models, fields, api, _
import base64
import io
from datetime import date
import xlsxwriter
from ..utils.employee_report_data import EmployeeReportData
from ..utils.salary_report_data import SalaryReportData


class HrReportsMtess(models.Model):
    _name = 'hr.reports.mtess'
    _inherit = ['mail.thread']
    _description = 'MTESS Reports'   

    name = fields.Char(
        string="Nombre",
        compute='_compute_name',
        store=True,
        readonly=True
    )
    year = fields.Selection(
        [(str(y), str(y)) for y in range(2000, fields.Date.today().year)],
        string='Año',
        required=True,
        default=lambda self: str(fields.Date.today().year - 1)
    )
    report_type = fields.Selection([
        ('employees', 'Planilla de Empleados y Obreros'),
        ('salaries', 'Planilla de Sueldos y Jornales'),
        ('summary', 'Resumen General de Personal Ocupado'),
    ], string='Report Type', required=True, default='employees')
    xlsx_output = fields.Binary(string='Archivo', )
    xlsx_filename = fields.Char(string='Nombre del Archivo', compute="_compute_filename", store=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Compañía",
        default=lambda self: self.env.company)

    @api.depends('year', 'report_type')
    def _compute_name(self):
        for record in self:
            if record.report_type and record.year:
                record.name = f"{record.year} - {dict(record._fields['report_type'].selection).get(record.report_type, '')}"
            else:
                record.name = ''
    
    @api.depends('name')
    def _compute_filename(self):
        for record in self:
            if record.name:
                record.xlsx_filename = f"{record.name}.xlsx"
            else:
                record.xlsx_filename = False
    
    def action_generate(self):
        self.ensure_one()
        report_title = dict(self._fields['report_type'].selection).get(self.report_type, 'Reporte')
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet(report_title)

        first_date = date(int(self.year), 1, 1)
        last_date = date(int(self.year), 12, 31)

        writer = getattr(self, f"_generate_{self.report_type}_data", None)
        writer and writer(worksheet, first_date, last_date)

        workbook.close()
        output.seek(0)
        file_content = output.read()

        self.write({
            'xlsx_output': base64.b64encode(file_content),
        })

    def _generate_employees_data(self, worksheet, first_date, last_date):
        headers = [
            "Nropatronal", "Documento", "Nombre", "Apellido", "Sexo", "Estadocivil",
            "Fechanac", "Nacionalidad", "Domicilio", "Fechanacmenor", "hijosmenores",
            "cargo", "profesion", "fechaentrada", "horariotrabajo", "menorescapa",
            "menoresescolar", "fechasalida", "motivosalida", "Estado"
        ]
        data = EmployeeReportData(self.env, first_date, last_date)

        # EmployeeReportEmployee attributes in order
        fields = [
            "patronal_number", "identification_number", "first_name", "last_name",
            "gender", "marital_status", "birth_date", "nationality", "address",
            "minor_birth_date", "minor_children", "job_title", "profession",
            "date_start", "work_schedule", "minor_date_start", "minor_school_status",
            "date_end", "end_reason"
        ]

        # Write headers
        for col, h in enumerate(headers):
            worksheet.write(0, col, h)

        # Write data rows
        for row, emp in enumerate(data.employees, start=1):
            values = [getattr(emp, f) for f in fields]
            for col, val in enumerate(values):
                worksheet.write(row, col, val)


    def _generate_salaries_data(self, worksheet, first_date, last_date):
        headers = [
            "Nropatronal","documento","formadepago","importeunitario",
           "h_ene","s_ene","h_feb","s_feb","h_mar","s_mar","h_abr","s_abr",
           "h_may","s_may","h_jun","s_jun","h_jul","s_jul","h_ago","s_ago",
           "h_set","s_set","h_oct","s_oct","h_nov","s_nov","h_dic","s_dic",
           "h_50","s_50","h_100","s_100","Aguinaldo","Beneficios",
           "Bonificaciones","Vacaciones","total_h","total_s","totalgeneral"
        ]
        data = SalaryReportData(self.env, first_date, last_date)

        # SalaryReportData attributes in order
        fields = [
            "patronal_number", "identification_number", "wage_type", "wage",
            "hours_january", "salary_january", "hours_february", "salary_february",
            "hours_march", "salary_march", "hours_april", "salary_april",
            "hours_may", "salary_may", "hours_june", "salary_june",
            "hours_july", "salary_july", "hours_august", "salary_august",
            "hours_september", "salary_september", "hours_october", "salary_october",
            "hours_november", "salary_november", "hours_december", "salary_december",
            "overtime_hours_50", "overtime_total_50", "overtime_hours_100", "overtime_total_100",
            "year_end_bonus", "benefits", "family_allowance", "vacation_pay",
            "hours_total", "salaries_total", "total"
        ]

        # Write headers
        for col, h in enumerate(headers):
            worksheet.write(0, col, h)

        # Write data rows
        for row, sal in enumerate(data.salaries, start=1):
            values = [getattr(sal, f) for f in fields]
            for col, val in enumerate(values):
                worksheet.write(row, col, val)


    def _generate_summary_data(self, worksheet, first_date, last_date):
        worksheet.write('A1', 'Employee Name')
        worksheet.write('B1', 'Department')
