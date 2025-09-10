from odoo import fields, api, models

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')
]

class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    has_currency = fields.Selection(CATEGORY_SELECTION, default="no", required=True, string="Currency")
    has_bank_account = fields.Selection(CATEGORY_SELECTION, default="no", required=True, string="Bank Account")
    approval_type = fields.Selection(selection_add=[('create_vendor_bill_adv', 'Create Vendor Bill for Advancement')])

    @api.onchange('approval_type')
    def _onchange_approval_type(self):
        super(ApprovalCategory, self)._onchange_approval_type()

        if self.approval_type == 'create_vendor_bill_adv':
            self.has_currency = self.has_amount = self.has_bank_account = 'required'
        else:
            self.has_currency = self.has_bank_account = 'no'