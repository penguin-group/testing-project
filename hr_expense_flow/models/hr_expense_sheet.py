from odoo import models, fields, api, _
from odoo.tools.misc import clean_context


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    # === Amount fields (in the expense's currency) === #
    total_amount_currency = fields.Monetary(
        string="Total",
        currency_field='currency_id',
        compute='_compute_amount_currency', store=True, readonly=True,
        tracking=True,
    )
    untaxed_amount_currency = fields.Monetary(
        string="Untaxed Amount",
        currency_field='currency_id',
        compute='_compute_amount_currency', store=True, readonly=True,
    )
    total_tax_amount_currency = fields.Monetary(
        string="Taxes",
        currency_field='currency_id',
        compute='_compute_amount_currency', store=True, readonly=True,
    )

    total_amount_parenthesized = fields.Char(
        string='Total Amount (Parenthesized)',
        compute='_compute_total_amount_parenthesized'
    )

    bank_account_id = fields.Many2one(
        'res.partner.bank',
        string='Bank Account',
        store=True,
        readonly=False,
        required=True
    )

    employee_related_partner_id = fields.Many2one(
        'res.partner',
        related='employee_id.user_partner_id',
        store=True
    )

    @api.depends('employee_id')
    def _compute_employee_bank_account(self):
        """Get the bank account set on the expense report."""
        for sheet in self:
            self.bank_account_id = sheet.employee_id.bank_account_id.id

    @api.depends('expense_line_ids.total_amount_currency', 'expense_line_ids.tax_amount_currency')
    def _compute_amount_currency(self):
        for sheet in self:
            sheet.total_amount_currency = sum(sheet.expense_line_ids.mapped('total_amount_currency'))
            sheet.total_tax_amount_currency = sum(sheet.expense_line_ids.mapped('tax_amount_currency'))
            sheet.untaxed_amount_currency = sheet.total_amount_currency - sheet.total_tax_amount_currency
    
    def _compute_total_amount_parenthesized(self):
        for rec in self:
            if rec.total_amount:
                rec.total_amount_parenthesized = f"({rec.company_currency_id.symbol} {rec.total_amount})"
            else:
                rec.total_amount_parenthesized = ""
    
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

        # if the expense report was paid by an employee, create a reimbursement invoice for them
        if self.payment_mode == 'own_account':
            reimbursement_amount = self.total_amount_currency  # amount to reimburse is taken from the report
            employee_invoice = expense._create_employee_reimbursement_invoice(reimbursement_amount, self.accounting_date)
            moves_sudo |= employee_invoice
            self.write({
                'account_move_ids': [(4, employee_invoice.id)]
            })

            # After self.write(), Odoo recomputes the invoice's fields, thus changing the bank account set on
            # the _create_employee_reimbursement_invoice() call. To avoid a whole method inheritance from the
            # account.move ecosystem just for this line, I just went ahead and overwrote the partner_bank_id
            # on the invoice.
            if self.bank_account_id:
                employee_invoice.partner_bank_id = self.bank_account_id

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

    def _get_employee_reimbursement_move(self):
        """Return the vendor bill for employee reimbursement."""
        clearing_journal = self.env.company.clearing_journal_id
        return self.account_move_ids.filtered(
            lambda m: m.move_type == "in_invoice" and m.journal_id == clearing_journal
        )[:1]

    @api.depends('account_move_ids.payment_state', 'account_move_ids.amount_residual')
    def _compute_from_account_move_ids(self):
        """[OVERRIDE] Full override of the _compute_from_account_move_ids method.

        Reason:
        - super() not used because we needed to replace the entire behavior of the method.
        - Business requirements:
            - Freeze payment_state as 'Paid' for approved expense reports immediately after approval.
            - Change payment_state depending on custom vendor bill's payment_state.

        Original method:
        - Location: 'addons/hr_expense/models/hr_expense_sheet.py'
        - Method: '_compute_from_account_move_ids'
        - Odoo Version: 18.0

        """
        for sheet in self:
            # If expense was NOT paid by the employee, payment_state remains as paid
            if sheet.payment_mode in ('company_account', 'petty_cash', 'credit_card') and sheet.approval_state in ('submit', 'approve'):
                sheet.amount_residual = 0.0
                sheet.payment_state = 'paid'
                continue

            if sheet.payment_mode == 'own_account':
                move = sheet._get_employee_reimbursement_move()
                if move:
                    sheet.payment_state = move.payment_state
                    sheet.amount_residual = move.amount_residual


    @api.depends('account_move_ids', 'payment_state', 'approval_state', 'payment_mode')
    def _compute_state(self):
        """[OVERRIDE] Full override of the _compute_state method.

        Reason:
        - super() not used because we needed to replace the entire behavior of the method.
        - Business requirements:
            - Freeze state for approved expense reports immediately after approval.
            - Add logic to modify state only with custom reimbursement vendor bill.

        Original method:
        - Location: 'addons/hr_expense/models/hr_expense_sheet.py'
        - Method: '_compute_state'
        - Odoo Version: 18.0

        """

        for sheet in self:
            if not sheet.approval_state:
                sheet.state = 'draft'
                continue
            if sheet.approval_state == 'cancel':
                sheet.state = 'cancel'
                continue

            # After manager approval, if the expense was not paid by the employee, the sheet state is directly set to Done.
            if sheet.approval_state == 'approve' and sheet.payment_mode != 'own_account':
                sheet.state = 'done'
                continue

            emp_reimbursement_move = sheet._get_employee_reimbursement_move()
            if emp_reimbursement_move:
                if sheet.payment_state != 'not_paid':
                    sheet.state = 'done'
                elif emp_reimbursement_move.state == 'draft':
                    sheet.state = 'approve'
                else:
                    sheet.state = 'post'
            else:
                sheet.state = sheet.approval_state  # Submit & approved without a move case

    @api.depends_context('uid')
    @api.depends('employee_id')
    def _compute_can_approve(self):
        """ Full override of '_compute_can_approve' method of the hr_expense module to add custom logic for approval checks."""

        is_team_approver = self.env.user.has_group('hr_expense.group_hr_expense_team_approver') or self.env.su
        is_approver = self.env.user.has_group('hr_expense.group_hr_expense_user') or self.env.su
        is_hr_admin = self.env.user.has_group('hr_expense.group_hr_expense_manager') or self.env.su

        for sheet in self:
            reason = False
            if not is_team_approver:
                reason = _("%s: Your are not a Manager or HR Officer", sheet.name)

            elif not is_hr_admin:
                sheet_employee = sheet.employee_id
                current_managers = sheet_employee.expense_manager_id \
                                   | sheet_employee.parent_id.user_id \
                                   | sheet_employee.department_id.manager_id.user_id \
                                   | sheet.user_id

                if self.env.user not in current_managers and not is_approver and sheet_employee.expense_manager_id.id != self.env.user.id:
                    reason = _("%s: It is not from your department", sheet.name)

            sheet.can_approve = not reason
            sheet.cannot_approve_reason = reason
