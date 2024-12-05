from odoo import models, fields, _, api
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def recompute_balance(self):
        for move in self:
            to_write = []
            for line in move.line_ids:
                to_write.append((1, line.id, {
                    'balance': line.company_id.currency_id.round(line.amount_currency / line.currency_rate)
                }))
            move.write({'line_ids': to_write})