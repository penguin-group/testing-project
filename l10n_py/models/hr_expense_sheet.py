from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import clean_context


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    def _do_create_moves(self):
        """
        Override original method to change the behavior of the "paid by the company" option. 
        It should create a vendor bill just like the "paid by the employee" option.
        """

        res = super(HrExpenseSheet, self)._do_create_moves()
        if self.create_vendor_bill:
            # Create a vendor bill and match with the created payment
            pass
        return res
   