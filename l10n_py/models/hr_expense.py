from odoo import models, fields


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    create_vendor_bill = fields.Boolean("Create Vendor Bill", default=True, help="Create a vendor bill for this expense and match it with the payment.")

