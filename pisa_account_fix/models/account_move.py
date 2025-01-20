import logging
from odoo import models, fields, api, _
from collections import Counter

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
                    if not partial['is_exchange'] and partial_id.debit_move_id:
                        partials.append({
                            'id': partial_id.id,
                            'line_id': partial_id.debit_move_id if partial_id.debit_move_id else False,
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
                        if move.amount_residual > 0 and partial['line_id'].amount_residual > 0:
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
            self.button_draft()
            self.action_post()
            _logger.info('Move %s reset successfully', self.name)
        except Exception as e:
            _logger.error('Error resetting move %s: %s', self.name, e)

    def mark_as_not_fixed(self):
        for move in self:
            move.write({'reconciliation_fixed': False})