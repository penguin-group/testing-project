from odoo import api, fields, models, release


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('currency_id', 'company_id', 'move_id.date')
    def _compute_currency_rate(self):
        # interfaces_tipo_cambio_compra_venta/models/account_move_line.py
        result = super(AccountMoveLine, self)._compute_currency_rate()
        for line in self:
            if line.move_id.currency_rate:
                if line.currency_id == line.move_id.currency_id:
                    old_quanity = line.quantity
                    line.secondary_currency_rate = 1 / line.move_id.currency_rate
                    line.quantity = old_quanity
        return result
        