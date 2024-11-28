from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    @api.depends('currency_id', 'company_id', 'move_id.invoice_currency_rate', 'move_id.date')
    def _compute_currency_rate(self):
        # Override original method to use account move rate for invoices
        for line in self:
            rate_type = 'buy' if line.move_id.is_inbound() else 'sell'
            if line.move_id.is_invoice(include_receipts=True):
                line.currency_rate = line.move_id.invoice_currency_rate
            elif line.currency_id:
                line.currency_rate = self.env['res.currency']._get_conversion_rate(
                    from_currency=line.company_currency_id,
                    to_currency=line.currency_id,
                    company=line.company_id,
                    date=line._get_rate_date(),
                    rate_type=rate_type,
                )
            else:
                line.currency_rate = 1

