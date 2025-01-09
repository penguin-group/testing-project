from odoo import models, api
from odoo.exceptions import ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.constrains('move_id')
    def _check_analytic_accounts(self):
        for payment in self:
            for line in payment.move_id.line_ids:
                if not line.analytic_account_id:
                    raise ValidationError(
                        "All payment lines must have an analytic account before registering."
                    )
