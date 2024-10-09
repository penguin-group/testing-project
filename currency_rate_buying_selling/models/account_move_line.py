from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    @api.depends('currency_id', 'company_id', 'move_id.date')
    def _compute_currency_rate(self):
    # Override original method to include the rate type in the context
        for line in self:
            rate_type = 'buying' if line.move_id.move_type == 'out_invoice' else 'selling'
            if line.currency_id:
                line = line.with_context(rate_type=rate_type)
                line.currency_rate = self.env['res.currency']._get_conversion_rate(
                    from_currency=line.company_currency_id,
                    to_currency=line.currency_id,
                    company=line.company_id,
                    date=line._get_rate_date(),
                )
            else:
                line.currency_rate = 1

