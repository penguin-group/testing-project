from odoo import models, fields, api, _
import base64
import io
from datetime import date
from odoo.exceptions import UserError
import xlsxwriter
from ..utils.employee_report_data import EmployeeReportData
from ..utils.salary_report_data import SalaryReportData
from ..utils.summary_report_data import SummaryReportData


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
    data = fields.Json("Data")
    xlsx_output = fields.Binary(string='Archivo', )
    xlsx_filename = fields.Char(string='Nombre del Archivo', compute="_compute_filename", store=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Compañía",
        default=lambda self: self.env.company)

    employees_report_headers = [
        "Nropatronal", "Documento", "Nombre", "Apellido", "Sexo", "Estadocivil",
        "Fechanac", "Nacionalidad", "Domicilio", "Fechanacmenor", "hijosmenores",
        "cargo", "profesion", "fechaentrada", "horariotrabajo", "menorescapa",
        "menoresescolar", "fechasalida", "motivosalida", "Estado"
    ]

    salaries_report_headers = [
        "Nropatronal","documento","formadepago","importeunitario",
        "h_ene","s_ene","h_feb","s_feb","h_mar","s_mar","h_abr","s_abr",
        "h_may","s_may","h_jun","s_jun","h_jul","s_jul","h_ago","s_ago",
        "h_set","s_set","h_oct","s_oct","h_nov","s_nov","h_dic","s_dic",
        "h_50","s_50","h_100","s_100","Aguinaldo","Beneficios",
        "Bonificaciones","Vacaciones","total_h","total_s","totalgeneral"
    ]
    summary_report_headers = [
        "Nropatronal", "anho", "supjefesvarones", "supjefesmujeres",
        "empleadosvarones", "empleadosmujeres", "obrerosvarones", "obrerosmujeres",
        "menoresvarones", "menoresmujeres", "orden"
    ]

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

        headers = getattr(self, f"{self.report_type}_report_headers")

        self._populate_data()
        self._write_to_worksheet(worksheet, headers, self.data)

        workbook.close()
        output.seek(0)
        file_content = output.read()

        self.write({
            'xlsx_output': base64.b64encode(file_content),
        })

    def _populate_data(self):
        first_date = date(int(self.year), 1, 1)
        last_date = date(int(self.year), 12, 31)

        self.data = [] # default

        report_map = {
            'employees': (EmployeeReportData, 'employees'),
            'salaries': (SalaryReportData, 'salaries'),
            'summary': (SummaryReportData, 'summary')
        }

        if self.report_type in report_map:
            cls, attr = report_map[self.report_type]
            report_data = cls(self.env, first_date, last_date)
            self.data = getattr(report_data, attr)


    def _write_to_worksheet(self, worksheet, headers, data):
        # Write headers
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)

        # Write rows
        for row, record in enumerate(data, start=1):
            for col, header in enumerate(headers):
                worksheet.write(row, col, record.get(header, ""))
