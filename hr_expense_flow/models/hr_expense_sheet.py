from odoo import models, fields, api
from odoo.tools.misc import clean_context


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    def _do_create_moves(self):
        """
        [OVERRIDE] Full override of '_do_create_moves' method to create vendor bills for expenses.
        
        Reason:
        - super() not used because we needed to replace the entire behavior of the method.
        - Business requirement: 
            - A vendor bill should be created for each expense.
            - The vendor bill should be created in the same journal as the one set in the expense settings page.
            - A journal entry should be created for each expense to act as a payment.
        
        Original method:
        - Location: 'addons/hr_expense/models/hr_expense_sheet.py'
        - Method: '_do_create_moves' method to create vendor bills for expenses.
        - Odoo Version: 18.0
        
        Modifications summary:
        - All the original code was removed and replaced with a new implementation.
        """
        
        self = self.with_context(clean_context(self.env.context))  # remove default_*
        moves_sudo = self.env['account.move']
        for expense in self.expense_line_ids:
            expense.sheet_id.accounting_date = expense.sheet_id.accounting_date or expense.sheet_id._calculate_default_accounting_date()
            move_sudo |= expense._create_vendor_bill()
        
        # returning the move with the super user flag set back as it was at the origin of the call
        return moves_sudo.sudo(self.env.su)