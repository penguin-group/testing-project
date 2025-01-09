from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.constrains('line_ids')
    def _check_analytic_accounts(self):
        for move in self:
            if move.is_invoice(include_receipts=True):  # Applies to both vendor and customer invoices
                for line in move.line_ids:
                    if not line.analytic_account_id:
                        raise ValidationError(
                            "All lines in the invoice must have an analytic account."
                        )

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    analytic_account_id = fields.Many2one(required=True)  # Enforce requirement at field level
