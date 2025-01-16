import logging
from odoo import models, fields, api, _

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
                partial_id = self.env['account.partial.reconcile'].browse(partial.get('partial_id'))
                if partial_id.exists():
                    if not partial['is_exchange'] and partial_id.debit_move_id:
                        partials.append({
                            'id': partial_id.id,
                            'line_id': partial_id.debit_move_id if partial_id.debit_move_id else False,
                        })
                    if remove_partials:
                        self.js_remove_outstanding_partial(partial_id.id)
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
                if partials:
                    _logger.info('Fixing reconciliation for move %s' % move.name)
                    for partial in partials:
                        # Reconcile
                        if move.amount_residual > 0:
                            move.reset_me()
                            partial['line_id'].move_id.reset_me()
                            move.js_assign_outstanding_line(partial['line_id'].id)
                            _logger.info('Reconciliation fixed for move %s' % move.name)
                move.reconciliation_fixed = True
            else:
                _logger.warning('Cannot fix reconciliation for move %s because it is related to an asset' % move.name)

    def _fix_incorrect_amount_fields(self):
        """
        Fix the incorrect amount fields for account moves and account move lines.
        """

        # account_move
        query = """
            UPDATE account_move 
            SET
            amount_untaxed_signed = amount_untaxed,
            amount_tax_signed = amount_tax,
            amount_total_signed = amount_total,
            amount_residual_signed = amount_residual
            WHERE 
            currency_id = 2
            AND company_id = 1
            AND (
                abs(amount_untaxed_signed) != abs(amount_untaxed)
                OR abs(amount_tax_signed) != abs(amount_tax)
                OR abs(amount_total_signed) != abs(amount_total) 
                OR abs(amount_residual_signed) != abs(amount_residual)
            )
        """
        try:
            self.env.cr.execute(query)
            self.env.cr.commit()
            _logger.info('Incorrect amount fields fixed for account moves')
        except Exception as e:
            self.env.cr.rollback()
            _logger.error('Error fixing incorrect amount fields for account moves: %s', e)

        # account_move_line
        query = """
            WITH calculated_base AS (
                SELECT
                    aml.id AS aml_id,
                    SUM(ABS(sub_aml.balance)) AS new_tax_base_amount
                FROM 
                    account_move_line aml
                JOIN 
                    account_move_line sub_aml
                    ON sub_aml.move_id = aml.move_id
                JOIN 
                    account_move_line_account_tax_rel amlatr 
                    ON amlatr.account_move_line_id = sub_aml.id
                JOIN 
                    account_tax tax 
                    ON tax.id = amlatr.account_tax_id
                WHERE
                    tax.amount != 0
                    AND tax.id = aml.tax_line_id
                GROUP BY aml.id
            )
            UPDATE 
                account_move_line aml
            SET 
                tax_base_amount = cb.new_tax_base_amount
            FROM 
                calculated_base cb
            WHERE 
                aml.id = cb.aml_id
                AND aml.company_id = 1
                AND aml.tax_base_amount != cb.new_tax_base_amount
        """
        try:
            self.env.cr.execute(query)
            self.env.cr.commit()
            _logger.info('Tax base amount updated successfully for account move lines')
        except Exception as e:
            self.env.cr.rollback()
            _logger.error('Error updating tax base amount for account move lines: %s', e)

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