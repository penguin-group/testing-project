from odoo import models, fields, api, _


class HrReportsMtess(models.Model):
    _name = 'hr.reports.mtess'
    _description = 'MTESS Reports'

    name = fields.Selection(
        [(str(y), str(y)) for y in range(2000, fields.Date.today().year)],
        string='Año',
        required=True,
        default=lambda self: str(fields.Date.today().year - 1)
    )
    report_employees = fields.Boolean('Planilla de Empleados y Obreros', default=True)
    report_salaries = fields.Boolean('Planilla de Sueldos y Jornales', default=True)
    report_summary = fields.Boolean('Resumen General de Personal Ocupado', default=True)
    line_ids = fields.One2many(
        comodel_name="hr.reports.mtess.line",
        inverse_name="mtess_report_id",
        string="Líneas"
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Compañía",
        default=lambda self: self.env.company)


class HrReportsMtessLine(models.Model):
    _name = 'hr.reports.mtess.line'
    _description = 'MTESS Report Line'

    def _get_default_name(self):
        if self.mtess_report_id and self.report_type:
            return self.mtess_report_id.name + " - " + dict(self._fields['report_type'].selection).get(self.report_type, '')
        return ''

    mtess_report_id = fields.Many2one(
        comodel_name="hr.reports.mtess",
        string="Reporte MTESS",
        required=True
    )
    report_type = fields.Selection([
        ('employees', 'Planilla de Empleados y Obreros'),
        ('salaries', 'Planilla de Sueldos y Jornales'),
        ('summary', 'Resumen General de Personal Ocupado'),
    ], string='Tipo de Reporte', required=True, default='employees')
    name = fields.Char(string="Nombre", default="_get_default_name", required=True)
    xlsx_output = fields.Binary(string='Archivo', )
    xlsx_filename = fields.Char(string='Nombre del Archivo', compute="_compute_filename")

    def _compute_filename(self):
        for rec in self:
            rec.xlsx_filename = rec.name + ".xlsx"

    def action_generate(self):
        pass  # Placeholder for future implementation
