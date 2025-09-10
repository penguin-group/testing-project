from odoo import models, _, fields
from odoo.exceptions import UserError


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    has_bank_account = fields.Selection(related="category_id.has_bank_account")
    has_currency = fields.Selection(related="category_id.has_currency")
    currency_id = fields.Many2one("res.currency", string="Currency")
    req_owner_related_partner_id = fields.Many2one(
        'res.partner',
        related='request_owner_id.partner_id',
        store=True
    )
    bank_account_id = fields.Many2one(
        "res.partner.bank",
        domain="[('partner_id', '=', req_owner_related_partner_id)]",
        string="Bank Account"
    )

    def action_confirm(self):
        super(ApprovalRequest, self).action_confirm()

        if self.currency_id.name != self.bank_account_id.currency_id.name:
            raise UserError(_("The approval request's currency (%s) doesn't match the bank account's currency (%s).",
                              self.currency_id.name, self.bank_account_id.currency_id.name))
