from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    company_secondary_currency_id = fields.Many2one(
        string='Company Secondary Currency',
        related='company_id.sec_currency_id', readonly=True,
    )
    invoice_secondary_currency_rate = fields.Float(
        string='Invoice Secondary Currency Rate',
        compute='_compute_invoice_secondary_currency_rate', store=True, precompute=True,
        copy=False,
        digits=0,
        help="Currency rate from company secondary currency to document currency.",
    )

    @api.depends('currency_id', 'company_secondary_currency_id', 'company_id', 'invoice_date', 'date')
    def _compute_invoice_secondary_currency_rate(self):
        for move in self:
            if move.company_currency_id != move.company_secondary_currency_id:
                move.invoice_secondary_currency_rate = self.env['res.currency']._get_conversion_rate(
                    from_currency=move.company_secondary_currency_id,
                    to_currency=move.company_currency_id,
                    company=move.company_id,
                    date=move.invoice_date or fields.Date.context_today(move),
                )
            else:
                move.invoice_secondary_currency_rate = 1
