from odoo import models, fields, api, _


class HrReportsMtessWizard(models.TransientModel):
    _name = 'hr.reports.mtess.wizard'
    _description = 'MTESS Report Wizard'

    year = fields.Selection(
        [(str(y), str(y)) for y in range(2000, fields.Date.today().year)],
        string='Year',
        required=True,
        default=lambda self: str(fields.Date.today().year - 1)
    )

    def action_generate_reports(self):
        self.ensure_one()
        for report_type in ['employees', 'salaries', 'summary']:
            self.env['hr.reports.mtess'].create({
                'year': self.year,
                'report_type': report_type,
            }).action_generate()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('MTESS Reports'),
            'res_model': 'hr.reports.mtess',
            'view_mode': 'list',
            'target': 'current',
            'context': {'group_by': ['year']},
        }   
