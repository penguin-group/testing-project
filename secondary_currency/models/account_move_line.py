from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'  

    company_secondary_currency_id = fields.Many2one(
        "res.currency",
        string='Company Secondary Currency',
        compute='_compute_company_secondary_currency_id', readonly=True, store=True, precompute=True,
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

    def _compute_company_secondary_currency_id(self):
        for line in self:
            line.company_secondary_currency_id = line.move_id.company_id.sec_currency_id

    @api.depends('currency_id', 'company_id', 'move_id.invoice_currency_rate', 'move_id.date')
    def _compute_secondary_currency_rate(self):
        for line in self:
            line.secondary_currency_rate = line.move_id.invoice_secondary_currency_rate

    @api.depends('balance','company_secondary_currency_id','currency_id','secondary_currency_rate','display_type',)
    def _compute_secondary_balance(self):
        for line in self:
            if line.company_secondary_currency_id and line.company_id.currency_exchange_journal_id != line.move_id.journal_id:
                # only process lines that are not in the currency exchange journal
                if line.display_type in ('line_section', 'line_note'):
                    line.secondary_balance = False
                elif line.currency_id == line.company_secondary_currency_id:
                    line.secondary_balance = line.company_secondary_currency_id.round(line.amount_currency)
                else:
                    line.secondary_balance = line.company_secondary_currency_id.round(line.balance / line.secondary_currency_rate)
            else:
                line.secondary_balance = 0
