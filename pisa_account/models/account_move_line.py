from odoo import models, fields, api, tools

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'  

    @api.depends('currency_id', 'company_id', 'move_id.invoice_currency_rate', 'move_id.date')
    def _compute_secondary_currency_rate(self):
        for line in self:
            line.secondary_currency_rate = line.move_id.invoice_secondary_currency_rate
    