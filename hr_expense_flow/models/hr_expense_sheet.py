from odoo import models, fields, api, _
from odoo.tools.misc import clean_context


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    # === Amount fields (in the expense's currency) === #
    total_amount_currency = fields.Monetary(
        string="Total in Currency",
        currency_field='currency_id',
        compute='_compute_amount_currency', store=True, readonly=True,
        tracking=True,
    )
    untaxed_amount_currency = fields.Monetary(
        string="Untaxed Amount in Currency",
        currency_field='currency_id',
        compute='_compute_amount_currency', store=True, readonly=True,
    )
    total_tax_amount_currency = fields.Monetary(
        string="Taxes in Currency",
        currency_field='currency_id',
        compute='_compute_amount_currency', store=True, readonly=True,
    )

    @api.depends('expense_line_ids.total_amount_currency', 'expense_line_ids.tax_amount_currency')
    def _compute_amount_currency(self):
        for sheet in self:
            sheet.total_amount_currency = sum(sheet.expense_line_ids.mapped('total_amount_currency'))
            sheet.total_tax_amount_currency = sum(sheet.expense_line_ids.mapped('tax_amount_currency'))
            sheet.untaxed_amount_currency = sheet.total_amount_currency - sheet.total_tax_amount_currency
    
    @api.depends('expense_line_ids.currency_id', 'company_currency_id')
    def _compute_currency_id(self):
        """
        Full override to remove the conditions that set the currency_id of the sheet to the company currency.
        """
        for sheet in self:
            if not sheet.expense_line_ids:
                sheet.currency_id = sheet.company_currency_id
            else:
                sheet.currency_id = sheet.expense_line_ids[:1].currency_id

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
        - Method: '_do_create_moves'
        - Odoo Version: 18.0
        
        Modifications summary:
        - All the original code was removed and replaced with a new implementation.
        """
        
        self = self.with_context(clean_context(self.env.context))  # remove default_*
        moves_sudo = self.env['account.move']
        for expense in self.expense_line_ids:
            expense.sheet_id.accounting_date = expense.sheet_id.accounting_date or expense.sheet_id._calculate_default_accounting_date()
            bill = expense._create_vendor_bill()
            moves_sudo |= bill
            moves_sudo |= expense._create_clearing_entry(bill.amount_total)
        
        # returning the move with the super user flag set back as it was at the origin of the call
        return moves_sudo.sudo(self.env.su)

    def action_open_account_moves(self):
        """
        [OVERRIDE] Full override of 'action_open_account_moves' method to open the journal entries related to the expense sheet.
        
        Reason:
        - super() not used because we needed to replace the entire behavior of the method.
        - Business requirement: When the user clicks on the "View Journal Entries" button, it should open
          all the journal entries related to the expense sheet. It should not open payment entries.
        
        Original method:
        - Location: 'addons/hr_expense/models/hr_expense_sheet.py'
        - Method: 'action_open_account_moves'
        - Odoo Version: 18.0
        
        Modifications summary:
        - [REMOVED] Skiped original code because it is adding payment entries to the action
        - [ADDED] Get all the journal entries
        """
        self.ensure_one()
        # [REMOVED] Skiped original code because it is adding payment entries to the action
        
        # [ADDED] Start: Get all the journal entries
        res_model = 'account.move'
        record_ids = self.account_move_ids
        # [ADDED] End

        action = {'type': 'ir.actions.act_window', 'res_model': res_model}
        if len(self.account_move_ids) == 1:
            action.update({
                'name': record_ids.name,
                'view_mode': 'form',
                'res_id': record_ids.id,
                'views': [(False, 'form')],
            })
        else:
            action.update({
                'name': _("Journal entries"),
                'view_mode': 'list',
                'domain': [('id', 'in', record_ids.ids)],
                'views': [(False, 'list'), (False, 'form')],
            })
        return action
    