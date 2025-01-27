import logging
from odoo import models, fields, api, _
from collections import Counter
from odoo.exceptions import UserError
from odoo.tools import format_amount, SQL
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    reconciliation_fixed = fields.Boolean(string='Reconciliation Fixed', default=False)
    
    def recompute_currency_rate(self):
        """
        Recompute the currency rate for the moves that have the invoice currency rate set to 1.
        """
        query = """
            UPDATE account_move 
            SET 
                invoice_currency_rate = (
                    SELECT rate 
                    FROM res_currency_rate 
                    WHERE currency_id = %s 
                    AND company_id = %s 
                    AND name <= account_move.date 
                    ORDER BY name DESC 
                    LIMIT 1
                )
            WHERE state = 'posted' 
            AND company_id = %s 
            AND currency_id = %s 
            AND invoice_currency_rate = 1
        """
        self.env.cr.execute(query, (
            self.env.ref('base.PYG').id, 
            1, 
            1, 
            self.env.ref('base.PYG').id
        ))
        self.env.cr.commit()
        _logger.info('Currency rate recomputed for moves with invoice currency rate set to 1')

    def get_partials(self, remove_partials=False):
        """
        Get the partials to reconcile for the invoice.
        """
        self.ensure_one()
        partials = []
        if self.invoice_payments_widget:
            for partial in self.invoice_payments_widget['content']:
                payment_id = self.env['account.payment'].browse(partial['account_payment_id'])
                bank_amls = self.env['account.move.line']
                if payment_id.journal_id.type == 'bank':
                    # Get the bank statement lines that are reconciled with the payment
                    all_line_ids = self.env['account.move.line']
                    all_line_ids |= payment_id.move_id.line_ids
                    all_line_ids |= payment_id.reconciled_statement_line_ids.line_ids
                    matching_numbers = all_line_ids.mapped('matching_number')
                    counts = Counter(matching_numbers)
                    matching_number = [item for item, count in counts.items() if count > 1]
                    if matching_number:
                        bank_amls |= all_line_ids.filtered(lambda l: l.matching_number == matching_number[0])
                partial_id = self.env['account.partial.reconcile'].browse(partial.get('partial_id'))
                if partial_id.exists():
                    partial_move_id = partial_id.debit_move_id if self.move_type == 'in_invoice' else partial_id.credit_move_id
                    if not partial['is_exchange'] and partial_move_id:
                        partials.append({
                            'id': partial_id.id,
                            'line_id': partial_move_id,
                            'bank_amls': bank_amls,
                        })
            if remove_partials:
                for partial in partials:
                    self.js_remove_outstanding_partial(partial['id'])
        return partials

    def _fix_reconciliation(self):
        record_len = len(self)
        cnt = 0
        for move in self:
            cnt +=1 
            if not move.asset_ids:
                percentage = (cnt / record_len) * 100
                _logger.info('Fixing reconciliation for move %s (%s/%s - %.2f%%)' % (move.name, cnt, record_len, percentage))
                partials = move.get_partials(remove_partials=True)
                move.reset_me()
                if partials:
                    for partial in partials:
                        partial['line_id'].move_id.reset_me()
                        # Reconcile
                        if move.amount_residual > 0 and abs(partial['line_id'].amount_residual) > 0:
                            move.js_assign_outstanding_line(partial['line_id'].id)
                            _logger.info('Reconciliation fixed for move %s' % move.name)
                            bank_amls = partial['bank_amls']
                            reconciled_bank_amls = bank_amls.filtered(lambda l: l.reconciled)
                            bank_amls -= reconciled_bank_amls
                            if bank_amls:
                                bank_amls.action_reconcile()
                move.reconciliation_fixed = True
            else:
                _logger.warning('Cannot fix reconciliation for move %s because it is related to an asset' % move.name)

    def reset_me(self):
        """
        Reset the moves.
        """
        self.ensure_one()
        try:
            unbalanced = self._get_secondary_unbalanced_moves()
            sec_balances = self.get_sec_balances()
            self.button_draft()
            if not unbalanced:
                self.restore_sec_balances(sec_balances)
            else:
                self.check_sec_balance()
            self.action_post()
            _logger.info('Move %s reset successfully', self.name)
        except Exception as e:
            raise UserError("Error resetting move %s: %s" % (self.name, e)) 

    def check_sec_balance(self):
        unbalanced = self._get_secondary_unbalanced_moves()
        if unbalanced:
            self.balance_move_lines(unbalanced[0])      

    def get_sec_balances(self):
        sec_balances = []
        for line in self.line_ids:
            sec_balances.append({
                'account_id': line.account_id.id,
                'balance': line.balance,
                'secondary_balance': line.secondary_balance
            })
        return sec_balances

    def restore_sec_balances(self, values):
        for line in self.line_ids:
            saved_line = next((item for item in values if item['account_id'] == line.account_id.id and item['balance'] == line.balance), None)
            if saved_line:
                line.secondary_balance = saved_line['secondary_balance']

    def mark_as_not_fixed(self):
        for move in self:
            move.write({'reconciliation_fixed': False})

    def balance_move_lines(self, unbalanced):
        """
        Balances the account.move.line by adjusting the secondary_balance field 
        to ensure the total balance is zero.
        """
        move = self.browse(unbalanced[0])
        total_balance = abs(unbalanced[1]) - abs(unbalanced[2])
        
        if total_balance == 0:
            return  # No adjustment needed

        lines = move.line_ids.filtered(lambda l: l.display_type not in ('line_section', 'line_note') and not l.reconciled)
            
        num_lines = len(lines)

        if num_lines == 0:
            raise ValueError("No lines to balance.")

        adjustment_per_line = total_balance / num_lines

        #Distribute the adjustment
        for line in lines:
            line.secondary_balance -= adjustment_per_line

        #Handle rounding differences
        unbalanced_moves = move._get_secondary_unbalanced_moves()
        if unbalanced_moves:
            unbalanced = unbalanced_moves[0]
            final_balance = abs(unbalanced[1]) - abs(unbalanced[2])
            if final_balance != 0:
                # Adjust the first line for rounding issues
                lines[0].secondary_balance -= final_balance

    def _check_secondary_balanced(self):
        ''' Assert the move is fully balanced on secondary balance.
        An error is raised if it's not the case.
        '''
        unbalanced_moves = self._get_secondary_unbalanced_moves()
        if unbalanced_moves:
            if unbalanced_moves and unbalanced_moves[0][1] + unbalanced_moves[0][2] == 0:
                return
            error_msg = _("An error has occurred.")
            for move_id, sum_debit, sum_credit in unbalanced_moves:
                move = self.browse(move_id)
                error_msg += _(
                    "\n\n"
                    "Secondary Balance in the move (%(move)s) is not balanced.\n"
                    "The total of debits equals %(debit_total)s and the total of credits equals %(credit_total)s.\n"
                    "The difference could be due to a rounding error in the secondary currency.\n"
                    "Please adjust it manually.\n",
                    move=move.display_name,
                    debit_total=format_amount(self.env, sum_debit, move.company_id.sec_currency_id),
                    credit_total=format_amount(self.env, sum_credit, move.company_id.sec_currency_id),
                    journal=move.journal_id.name)
            raise UserError(error_msg)
