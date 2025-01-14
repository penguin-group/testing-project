import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def update_signed_amounts(self):
        """
        Update the signed amounts for the moves that have the same currency as the company currency.
        """
        moves = self.env['account.move'].search([('state', '=', 'posted')])
        # Filter moves that have the same currency as the company currency and have different signed amounts
        moves = moves.filtered(lambda m: 
            m.currency_id.id == m.company_id.currency_id.id 
            and (
                abs(m.amount_untaxed) != abs(m.amount_untaxed_signed) or
                abs(m.amount_tax) != abs(m.amount_tax_signed) or 
                abs(m.amount_total) != abs(m.amount_total_signed) or 
                abs(m.amount_residual) != abs(m.amount_residual_signed)
            )
        )
        cnt = 0
        len_moves = len(moves)
        for move in moves:
            cnt += 1
            percentage = (cnt / len_moves) * 100
            _logger.info('Processing move %s (%s/%s - %.2f%%)' % (move.name, cnt, len_moves, percentage))
            if move.amount_untaxed_signed >= 0:
                move.amount_untaxed_signed = abs(move.amount_untaxed)
            else:
                move.amount_untaxed_signed = -abs(move.amount_untaxed)
            
            if move.amount_tax_signed >= 0:
                move.amount_tax_signed = abs(move.amount_tax)
            else:
                move.amount_tax_signed = -abs(move.amount_tax)
            
            if move.amount_total_signed >= 0:
                move.amount_total_signed = abs(move.amount_total)
            else:
                move.amount_total_signed = -abs(move.amount_total)
            
            if move.amount_residual_signed >= 0:
                move.amount_residual_signed = abs(move.amount_residual)
            else:
                move.amount_residual_signed = -abs(move.amount_residual)

    def recompute_currency_rate(self):
        """
        Recompute the currency rate for the moves that have the invoice currency rate set to 1.
        """
        query = """
            UPDATE account_move 
            SET invoice_currency_rate = (
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
        for partial in self.invoice_payments_widget['content']:
            partial_id = self.env['account.partial.reconcile'].browse(partial.get('partial_id'))
            if partial_id.exists():
                if not partial['is_exchange'] and partial_id.debit_move_id:
                    partials.append({
                        'id': partial_id.id,
                        'line_id': partial_id.debit_move_id.id if partial_id.debit_move_id else False,
                    })
                if remove_partials:
                    self.js_remove_outstanding_partial(partial_id.id)
        return partials

    def _fix_reconciliation(self):
        record_len = len(self)
        cnt = 0
        for move in self:
            cnt +=1 
            if not move.asset_ids: # We cannot fix reconciliation for moves related to assets
                percentage = (cnt / record_len) * 100
                _logger.info('Fixing reconciliation for move %s (%s/%s - %.2f%%)' % (move.name, cnt, record_len, percentage))
                partials = move.get_partials(remove_partials=True)
                if partials:
                    _logger.info('Fixing reconciliation for move %s' % move.name)
                    for partial in partials:
                        # Reconcile
                        if move.amount_residual > 0:
                            move.js_assign_outstanding_line(partial['line_id'])
