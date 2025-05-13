from odoo import models, fields, api, Command


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    def _create_vendor_bill(self):
        """Create a vendor bill for this expense."""
        self.ensure_one()
        invoice_vals = {
            'expense_sheet_id': self.sheet_id.id,
            'move_type': 'in_invoice',
            'journal_id': self.sheet_id.journal_id.id, # The default value in this field should be the journal set in the expense settings page.
            'partner_id': self.vendor_id.id,
            'currency_id': self.sheet_id.currency_id.id,
            'invoice_date': fields.Date.context_today(self),
            'line_ids': [Command.create(self._prepare_move_lines_vals())],
            'attachment_ids': [
                Command.create(attachment.copy_data({'res_model': 'account.move', 'res_id': False, 'raw': attachment.raw})[0])
                for attachment in self.message_main_attachment_id
            ],
        }
        bill = self.env['account.move'].sudo().create(invoice_vals)
        self._fix_move_lines(bill)
        return bill

    def _fix_move_lines(self, bill):
        self.ensure_one()
        # Fix credit account
        credit_line = bill.line_ids.filtered(lambda line: line.credit > 0)
        if credit_line:
            credit_line.write({
                'account_id': self.company_id.expense_reimbursement_account_id.id,
                'partner_id': self.vendor_id.id,
            })
        
    def _create_clearing_entry(self, total_amount):
        self.ensure_one()
        line_ids = []
        if self.payment_mode == 'company_account':
            
            # Get the current balance of the outstanding account for this employee
            balance = self.env['account.move.line'].sudo().search([
                ('account_id', '=', self.company_id.expense_outstanding_account_id.id),
                ('partner_id', '=', self.employee_id.work_contact_id.id),
                ('move_id.state', '=', 'posted')
            ]).mapped('balance')
            outstanding_balance = sum(balance)

            # Create a debit line for the total amount of the expense
            # The account should be the expense reimbursement account
            line_ids.append(
                Command.create({
                    'debit': total_amount,
                    'account_id': self.company_id.expense_reimbursement_account_id.id,
                    'partner_id': self.vendor_id.id,
                }), 
            )
            
            # If the balance is less than the total amount, create an additional line to record the difference 
            # as a credit to the employee's account (reimbursement payable account)
            if outstanding_balance < total_amount:
                line_ids.append(
                    Command.create({
                        'credit': total_amount - outstanding_balance,
                        'account_id': self.company_id.expense_reimbursement_account_id.id,
                        'partner_id': self.employee_id.work_contact_id.id,
                    })
                )
                credit = outstanding_balance
            else:
                credit = total_amount
            # Create a credit line for the outstanding balance 
            line_ids.append(
                Command.create({
                    'credit': credit,
                    'account_id': self.company_id.expense_outstanding_account_id.id,
                    'partner_id': self.employee_id.work_contact_id.id,
                }),
            )

        move_vals = {
            'move_type': 'entry',
            'expense_sheet_id': self.sheet_id.id,
            'date': fields.Date.context_today(self),
            'journal_id': self.sheet_id.journal_id.id,
            'ref': f'Clearing entry for expense {self.name}',
            'line_ids': line_ids
        }
        clearing_entry = self.env['account.move'].sudo().create(move_vals)
        clearing_entry.action_post()
        return clearing_entry
