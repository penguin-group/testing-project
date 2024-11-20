from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'  

    @api.depends('currency_id', 'company_id', 'move_id.date')
    def _compute_secondary_currency_rate(self):
        for line in self:
            if line.currency_id:
                conversion_method = self.env['res.currency']._get_buying_conversion_rate if line.move_id.move_type == 'out_invoice' and line.currency_id == line.company_currency_id and line.currency_id != line.company_secondary_currency_id else self.env['res.currency']._get_conversion_rate
                line.secondary_currency_rate = conversion_method(
                    from_currency=line.company_secondary_currency_id,
                    to_currency=line.currency_id,
                    company=line.company_id,
                    date=line._get_rate_date(),
                )
            else:
                line.secondary_currency_rate = 1

