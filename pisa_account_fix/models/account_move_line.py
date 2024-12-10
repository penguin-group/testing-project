from odoo import models, fields, api, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('currency_id', 'company_id', 'move_id.date')
    def _compute_currency_rate(self):
        # Override this method to fix currency rate and balance in asset depreciation moves
        for line in self:
            if line.currency_id:
                date = line.move_id.asset_id.acquisition_date if line.move_id.asset_id else line._get_rate_date()
                line.currency_rate = self.env['res.currency']._get_conversion_rate(
                    from_currency=line.company_currency_id,
                    to_currency=line.currency_id,
                    company=line.company_id,
                    date=date,
                )
            else:
                line.currency_rate = 1