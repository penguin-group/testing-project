from odoo import models, api, fields


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
