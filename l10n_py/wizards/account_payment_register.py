from odoo import models, api

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payment_vals_from_wizard(self, batch_result):
        rate_type = 'buy' if self.payment_type == 'inbound' else 'sell'
        payment_vals = {
            'date': self.payment_date,
            'amount': self.amount,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_bank_id': self.partner_bank_id.id,
            'payment_method_line_id': self.payment_method_line_id.id,
            'destination_account_id': self.line_ids[0].account_id.id,
            'write_off_line_vals': [],
        }

        if self.payment_difference_handling == 'reconcile':
            if self.early_payment_discount_mode:
                epd_aml_values_list = []
                for aml in batch_result['lines']:
                    if aml.move_id._is_eligible_for_early_payment_discount(self.currency_id, self.payment_date):
                        epd_aml_values_list.append({
                            'aml': aml,
                            'amount_currency': -aml.amount_residual_currency,
                            'balance': aml.currency_id._convert(-aml.amount_residual_currency, aml.company_currency_id, date=self.payment_date, rate_type=rate_type),
                        })

                open_amount_currency = self.payment_difference * (-1 if self.payment_type == 'outbound' else 1)
                open_balance = self.currency_id._convert(open_amount_currency, self.company_id.currency_id, self.company_id, self.payment_date, rate_type=rate_type)
                early_payment_values = self.env['account.move']._get_invoice_counterpart_amls_for_early_payment_discount(epd_aml_values_list, open_balance)
                for aml_values_list in early_payment_values.values():
                    payment_vals['write_off_line_vals'] += aml_values_list

            elif not self.currency_id.is_zero(self.payment_difference):

                if self.writeoff_is_exchange_account:
                    # Force the rate when computing the 'balance' only when the payment has a foreign currency.
                    # If not, the rate is forced during the reconciliation to put the difference directly on the
                    # exchange difference.
                    if self.currency_id != self.company_currency_id:
                        payment_vals['force_balance'] = sum(batch_result['lines'].mapped('amount_residual'))
                else:
                    if self.payment_type == 'inbound':
                        # Receive money.
                        write_off_amount_currency = self.payment_difference
                    else:  # if self.payment_type == 'outbound':
                        # Send money.
                        write_off_amount_currency = -self.payment_difference

                    payment_vals['write_off_line_vals'].append({
                        'name': self.writeoff_label,
                        'account_id': self.writeoff_account_id.id,
                        'partner_id': self.partner_id.id,
                        'currency_id': self.currency_id.id,
                        'amount_currency': write_off_amount_currency,
                        'balance': self.currency_id._convert(write_off_amount_currency, self.company_id.currency_id, self.company_id, self.payment_date, rate_type=rate_type),
                    })

        return payment_vals

    def _get_total_amount_in_wizard_currency_to_full_reconcile(self, batch_result, early_payment_discount=True):
        rate_type = 'buy' if self.payment_type == 'inbound' else 'sell'
        """ Compute the total amount needed in the currency of the wizard to fully reconcile the batch of journal
        items passed as parameter.

        :param batch_result:    A batch returned by '_get_batches'.
        :return:                An amount in the currency of the wizard.
        """
        self.ensure_one()

        comp_curr = self.company_id.currency_id
        if self.source_currency_id == self.currency_id:
            # Same currency (manage the early payment discount).
            return self._get_total_amount_using_same_currency(batch_result, early_payment_discount=early_payment_discount)
        elif self.source_currency_id != comp_curr and self.currency_id == comp_curr:
            # Foreign currency on source line but the company currency one on the opposite line.
            return self.source_currency_id._convert(
                self.source_amount_currency,
                comp_curr,
                self.company_id,
                self.payment_date,
                rate_type=rate_type,
            ), False
        elif self.source_currency_id == comp_curr and self.currency_id != comp_curr:
            # Company currency on source line but a foreign currency one on the opposite line.
            residual_amount = 0.0
            for aml in batch_result['lines']:
                if not aml.move_id.original_payment_id and not aml.move_id.statement_line_id:
                    conversion_date = self.payment_date
                else:
                    conversion_date = aml.date
                residual_amount += comp_curr._convert(
                    aml.amount_residual,
                    self.currency_id,
                    self.company_id,
                    conversion_date,
                    rate_type=rate_type,
                )
            return abs(residual_amount), False
        else:
            # Foreign currency on payment different than the one set on the journal entries.
            return comp_curr._convert(
                self.source_amount,
                self.currency_id,
                self.company_id,
                self.payment_date,
                rate_type=rate_type,
            ), False
    