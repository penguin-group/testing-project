from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_currency_rate = fields.Float(
        string='Invoice Currency Rate',
        compute='_compute_invoice_currency_rate', store=True, precompute=True,
        copy=False,
        digits=0,
        help="Currency rate from company currency to document currency.",
    )

    @api.depends('currency_id', 'company_currency_id', 'company_id', 'invoice_date')
    def _compute_invoice_currency_rate(self):
        for move in self:
            if move.is_invoice(include_receipts=True):
                if move.currency_id:
                    move.invoice_currency_rate = self.env['res.currency']._get_conversion_rate(
                        from_currency=move.company_currency_id,
                        to_currency=move.currency_id,
                        company=move.company_id,
                        date=move.invoice_date or fields.Date.context_today(move),
                    )
                else:
                    move.invoice_currency_rate = 1