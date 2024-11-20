from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'  

    company_secondary_currency_id = fields.Many2one(
        string='Company Secondary Currency',
        related='move_id.company_secondary_currency_id', readonly=True, store=True, precompute=True,
    )
    secondary_currency_rate = fields.Float(
        compute='_compute_secondary_currency_rate',
        help="Currency rate from company secondary currency to document currency.",
    )
    secondary_balance = fields.Monetary(
        string='Secondary Balance',
        compute='_compute_secondary_balance', store=True, readonly=False, precompute=True,
        currency_field='company_secondary_currency_id',
        tracking=True,
    )

    @api.depends('currency_id', 'company_id', 'move_id.date')
    def _compute_secondary_currency_rate(self):
        for line in self:
            if line.currency_id:
                line.secondary_currency_rate = self.env['res.currency']._get_conversion_rate(
                    from_currency=line.company_secondary_currency_id,
                    to_currency=line.currency_id,
                    company=line.company_id,
                    date=line._get_rate_date(),
                )
            else:
                line.secondary_currency_rate = 1

    @api.depends('balance')
    def _compute_secondary_balance(self):
        for line in self:
            if line.display_type in ('line_section', 'line_note'):
                line.secondary_balance = False
            else:
                line.secondary_balance = line.balance / line.secondary_currency_rate
                if line.currency_id == line.company_secondary_currency_id:
                    line.secondary_balance = line.amount_currency
