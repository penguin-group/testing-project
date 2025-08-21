from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import io
import xlsxwriter
from datetime import date


class HrReportsMtessWizard(models.TransientModel):
    _name = 'hr.reports.mtess.wizard'
    _description = 'MTESS HR Reports Wizard'

    report_type = fields.Selection([
        ('employees', 'Planilla de Empleados y Obreros'),
        ('salaries', 'Planilla de Sueldos y Jornales'),
        ('summary', 'Resumen General de Personal Ocupado'),
    ], string='Tipo de Reporte', required=True)
    year = fields.Selection(
        [(str(y), str(y)) for y in range(2000, fields.Date.today().year)],
        string='Año',
        required=True,
        default=lambda self: str(fields.Date.today().year - 1)
    )
    file_data = fields.Binary('Archivo Excel')
    file_name = fields.Char('Nombre del Archivo')

    def action_generate_excel(self):
        self.ensure_one()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Reporte')

        # Example: Write report title
        worksheet.write(0, 0, dict(self._fields['report_type'].selection)[self.report_type])

        # TODO: Add logic to fill worksheet according to self.report_type
        first_date = date(int(self.year), 1, 1)
        last_date = date(int(self.year), 12, 31)

        workbook.close()
        output.seek(0)
        file_content = output.read()
        file_name = f"{self.report_type}_mtess.xlsx"

        self.write({
            'file_data': base64.b64encode(file_content),
            'file_name': file_name,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/{self._name}/{self.id}/file_data/{file_name}?download=true",
            'target': 'self',
        }