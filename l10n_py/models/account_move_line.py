from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    @api.depends('currency_id', 'company_id', 'move_id.invoice_currency_rate', 'move_id.date')
    def _compute_currency_rate(self):
        # Override original method to use invoice_currency_rate of the journal entry
        for line in self:
            line.currency_rate = line.move_id.invoice_currency_rate

