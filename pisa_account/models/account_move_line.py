from odoo import models, fields, api, tools

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'  

    @api.depends('currency_id', 'company_id', 'move_id.invoice_currency_rate', 'move_id.date')
    def _compute_secondary_currency_rate(self):
        for line in self:
            line.secondary_currency_rate = line.move_id.invoice_secondary_currency_rate

    @api.depends('balance')
    def _compute_secondary_balance(self):
        # Override the original method from the secondary_currency module to modify the rounding, 
        # which should be 0 decimal places, although the rounding field in the currency settings is set to two decimal places.
        for line in self:
            company_secondary_currency_id = line.company_id.sec_currency_id
            if company_secondary_currency_id:
                if line.display_type in ('line_section', 'line_note'):
                    line.secondary_balance = False
                elif line.currency_id == company_secondary_currency_id:
                    if company_secondary_currency_id.name == "PYG":
                        line.secondary_balance = tools.float_round(line.amount_currency, 0)
                    else:
                        line.secondary_balance = company_secondary_currency_id.round(line.amount_currency)
                else:
                    if company_secondary_currency_id.name == "PYG":
                        line.secondary_balance = tools.float_round(line.balance / line.secondary_currency_rate, 0)
                    else:
                        line.secondary_balance = company_secondary_currency_id.round(line.balance / line.secondary_currency_rate)
            else:
                line.secondary_balance = 0