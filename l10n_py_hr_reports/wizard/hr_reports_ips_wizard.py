from odoo import models, fields, api, _


class HrReportsIPSWizard(models.TransientModel):
    _name = 'hr.reports.ips.wizard'
    _description = 'IPS Report Wizard'

    year = fields.Selection(
        [(str(y), str(y)) for y in range(2000, fields.Date.today().year + 1)],
        string='Year',
        required=True,
        default=lambda self: str(fields.Date.today().year)
    )
    month = fields.Selection(
        [(str(m), str(m)) for m in range(1, 13)],
        string="Month",
        required=True,
        default=lambda self: str(fields.Date.today().month)
    )

    def action_generate_report(self):
        self.ensure_one()
        self.env['hr.reports.ips'].create({
            'year': self.year,
            'month': self.month,
        }).action_generate()
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('IPS Reports'),
            'res_model': 'hr.reports.ips',
            'view_mode': 'list',
            'target': 'current',
            'context': {'group_by': ['year']},
        }   
