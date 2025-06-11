from odoo import models, fields, api, Command


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    outstanding_balance = fields.Monetary(
        string='Outstanding Balance',
        compute='_compute_outstanding_balance',
        currency_field='company_currency_id',
    )

    payment_mode = fields.Selection(
        selection_add=[('petty_cash', 'Petty Cash')],
        ondelete={'petty_cash': 'set default'},
    )

    petty_cash_account_id = fields.Many2one(
        'account.account',
        string='Petty Cash Account',
    )

    petty_cash_account_ids = fields.Many2many(
        comodel_name='account.account',
        string='Petty Cash Accounts',
        help='Select accounts for petty cash.',
        compute='_compute_petty_cash_accounts',
        store=True,
    )

    @api.onchange('payment_mode', 'employee_id')
    def _compute_petty_cash_accounts(self):
        for expense in self.filtered(lambda e: e.state == 'draft'):
            expense.petty_cash_account_id = False
            if expense.payment_mode == 'petty_cash' and expense.employee_id:
                expense.petty_cash_account_ids = expense.employee_id.department_id.petty_cash_account_ids
            else:
                expense.petty_cash_account_ids = self.env['account.account']

    @api.constrains('payment_mode')
    def _check_petty_cash_constraints(self):
        for expense in self:
            if expense.payment_mode == 'petty_cash':
                if not self.employee_id:
                    raise ValueError("Petty Cash payment mode requires the expense to be linked to an employee.")
                if not self.employee_id.department_id:
                    raise ValueError("The employee linked to the expense must belong to a department.")
                if not self.employee_id.department_id.petty_cash_account_ids:
                    raise ValueError("The department linked to the employee must have petty cash accounts set up.")

    @api.depends('employee_id', 'currency_id', 'total_amount', 'total_amount_currency')
    def _compute_outstanding_balance(self):
        for expense in self:
            if not expense.employee_id:
                expense.outstanding_balance = 0
                continue
            balance = self.env['account.move.line'].sudo().search([
                ('account_id', '=', expense.company_id.expense_outstanding_account_id.id),
                ('partner_id', '=', expense.employee_id.work_contact_id.id),
                ('move_id.state', '=', 'posted')
            ]).mapped('balance')
            expense.outstanding_balance = sum(balance)

    def _create_vendor_bill(self):
        """Create a vendor bill for this expense."""
        self.ensure_one()
        invoice_vals = {
            'expense_sheet_id': self.sheet_id.id,
            'move_type': 'in_invoice',
            'journal_id': self.company_id.expense_journal_id.id,
            'partner_id': self.vendor_id.id,
            'currency_id': self.currency_id.id,
            'invoice_date': fields.Date.context_today(self),
            'line_ids': [Command.create(self._prepare_vendor_bill_line_vals())],
            'attachment_ids': [
                Command.create(attachment.copy_data({'res_model': 'account.move', 'res_id': False, 'raw': attachment.raw})[0])
                for attachment in self.message_main_attachment_id
            ],
        }
        bill = self.env['account.move'].sudo().create(invoice_vals)
        self._fix_move_lines(bill)
        return bill

    def _prepare_vendor_bill_line_vals(self):
        self.ensure_one()
        account = self._get_base_account()

        return {
            'name': self._get_move_line_name(),
            'account_id': account.id,
            'quantity': self.quantity or 1,
            'price_unit': self.total_amount_currency,
            'currency_id': self.currency_id.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'analytic_distribution': self.analytic_distribution,
            'expense_id': self.id,
            'partner_id': False if self.payment_mode == 'company_account' else self.employee_id.sudo().work_contact_id.id,
            'tax_ids': [Command.set(self.tax_ids.ids)],
        }

    def _fix_move_lines(self, bill):
        self.ensure_one()
        # Fix credit account
        credit_line = bill.line_ids.filtered(lambda line: line.credit > 0)
        if credit_line:
            credit_line.write({
                'account_id': self.company_id.expense_reimbursement_account_id.id,
                'partner_id': self.vendor_id.id
            })
        
    def _create_clearing_entry(self, total_amount):
        self.ensure_one()
        
        line_ids = []
        
        # Create a debit line for the total amount of the expense
        # The account should be the expense reimbursement account (to Vendor)
        line_ids.append(
            Command.create({
                'amount_currency': total_amount, # debit
                'currency_id': self.currency_id.id,
                'account_id': self.company_id.expense_reimbursement_account_id.id,
                'partner_id': self.vendor_id.id,
            }), 
        )

        if self.payment_mode == 'company_account':
            # If the balance is less than the total amount, create an additional line to record the difference 
            # as a credit to the employee's account (reimbursement payable account)
            outstanding_balance_currency = self.company_currency_id._convert(
                self.outstanding_balance,
                self.currency_id,
                self.company_id,
                self.date or fields.Date.context_today(self),
            )
            if outstanding_balance_currency < total_amount:
                line_ids.append(
                    Command.create({
                        'amount_currency': -(total_amount - outstanding_balance_currency), # credit
                        'currency_id': self.currency_id.id,
                        'account_id': self.company_id.expense_reimbursement_account_id.id,
                        'partner_id': self.employee_id.work_contact_id.id,
                    })
                )
                credit = outstanding_balance_currency
            else:
                credit = total_amount
            
            # Create a credit line for the outstanding balance 
            line_ids.append(
                Command.create({
                    'amount_currency': -credit, # credit
                    'currency_id': self.currency_id.id,
                    'account_id': self.company_id.expense_outstanding_account_id.id,
                    'partner_id': self.employee_id.work_contact_id.id,
                }),
            )
        elif self.payment_mode == 'own_account': 
            # Create a credit line for the total amount of the expense
            # The account should be the expense reimbursement account (to Employee)
            line_ids.append(
                Command.create({
                    'amount_currency': -total_amount, # credit
                    'currency_id': self.currency_id.id,
                    'account_id': self.company_id.expense_reimbursement_account_id.id,
                    'partner_id': self.employee_id.work_contact_id.id,
                }),
            )
        elif self.payment_mode == 'petty_cash':
            # Create a credit line for the total amount of the expense
            # The account should be the petty cash account
            line_ids.append(
                Command.create({
                    'amount_currency': -total_amount, # credit
                    'currency_id': self.currency_id.id,
                    'account_id': self.petty_cash_account_id.id,
                }),
            )

        move_vals = {
            'move_type': 'entry',
            'currency_id': self.currency_id.id,
            'expense_sheet_id': self.sheet_id.id,
            'date': fields.Date.context_today(self),
            'journal_id': self.company_id.clearing_journal_id.id,
            'ref': f'Clearing entry for expense {self.name}',
            'line_ids': line_ids
        }
        clearing_entry = self.env['account.move'].sudo().create(move_vals)
        clearing_entry.action_post()
        return clearing_entry
