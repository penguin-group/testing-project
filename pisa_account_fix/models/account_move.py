import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def update_signed_amounts(self):
        moves = self.env['account.move'].search([('state', '=', 'posted')])
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

    def _fix_reconciliation(self):
        record_len = len(self)
        cnt = 0

        for move in self:
            cnt +=1 
            if not move.asset_ids: # We cannot fix reconciliation for moves related to assets
                partials = []
                percentage = (cnt / record_len) * 100
                _logger.info('Fixing reconciliation for move %s (%s/%s - %.2f%%)' % (move.name, cnt, record_len, percentage))
                for partial in move.invoice_payments_widget['content']:
                    partial_id = self.env['account.partial.reconcile'].browse(partial.get('partial_id'))
                    if not partial['is_exchange'] and partial_id.debit_move_id:
                        partials.append({
                            'id': partial_id.id,
                            'line_id': partial_id.debit_move_id.id if partial_id.debit_move_id else False,
                        })
                        # Remove partial
                        move.js_remove_outstanding_partial(partial_id.id)
                # Compute invoice currency rate
                if move.currency_id.name == "PYG" and move.company_id.currency_id.name == "USD" and move.invoice_currency_rate == 1:
                    _logger.info('Fixing invoice currency rate for move %s' % move.name)
                    amount_company_currency = abs(sum(move.line_ids.mapped('credit')))
                    move.button_draft()
                    currency_rate = round(move.amount_total / amount_company_currency, 2)
                    move.invoice_currency_rate = currency_rate
                    move.action_post()
                _logger.info('Fixing reconciliation for move %s' % move.name)
                for partial in partials:
                    # Reconcile
                    if move.amount_residual > 0:
                        move.js_assign_outstanding_line(partial['line_id'])