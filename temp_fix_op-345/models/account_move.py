from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import format_amount, SQL

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _post(self, soft=True):
        ''' Override to compute the secondary balance before posting the move.
        '''
        if self.env.context.get('move_reverse_cancel'):
            self.line_ids._compute_secondary_balance()
        return super(AccountMove, self)._post(soft)