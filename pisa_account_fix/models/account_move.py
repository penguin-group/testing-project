from odoo import models, fields, _, api
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def recompute_balance(self):
        for move in self.filtered(lambda m: m.line_ids.filtered(lambda l: l.credit == 0 and l.debit == 0)):
            try:
                to_write = []
                for line in move.line_ids:
                    to_write.append((1, line.id, {
                        'balance': line.company_id.currency_id.round(line.amount_currency / line.currency_rate)
                    }))
                move.write({'line_ids': to_write})
            except Exception as e:
                raise UserError(_('Error: %s') % e)