from odoo import fields, api, models

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')
]

class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    has_currency = fields.Selection(CATEGORY_SELECTION, default="no", required=True, string="Currency")
    has_bank_account = fields.Boolean(default=False, required=True, string="Has Bank Account")