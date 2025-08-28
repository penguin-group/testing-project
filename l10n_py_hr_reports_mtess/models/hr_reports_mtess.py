from odoo import models, fields, api, _
import base64
import io
from datetime import date
import xlsxwriter


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
        worksheet.write('A1', 'Employee Name')
        worksheet.write('B1', 'Department')


    def _generate_salaries_data(self, worksheet, first_date, last_date):
        worksheet.write('A1', 'Employee Name')
        worksheet.write('B1', 'Department')

    def _generate_summary_data(self, worksheet, first_date, last_date):
        worksheet.write('A1', 'Employee Name')
        worksheet.write('B1', 'Department')
