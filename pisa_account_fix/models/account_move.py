from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _fix_reconciliation(self):
        for move in self:
            if not move.asset_ids: # We cannot fix reconciliation for moves related to assets
                partials = []
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
                    print('Fixing invoice currency rate for move %s' % move.name)
                    move.button_draft()
                    move._compute_invoice_currency_rate()
                    move.action_post()
                print('Fixing reconciliation for move %s' % move.name)
                for partial in partials:
                    # Reconcile
                    move.js_assign_outstanding_line(partial['line_id'])