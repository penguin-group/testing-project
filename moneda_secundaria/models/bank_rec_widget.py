from odoo import _, api, fields, models, tools, Command


class BankWidget(models.Model):
    _inherit='bank.rec.widget'

    def _action_validate(self):
        self.ensure_one()
        partners = (self.line_ids.filtered(lambda x: x.flag != 'liquidity')).partner_id
        partner_to_set = partners if len(partners) == 1 else self.env['res.partner']

        # Prepare the lines to be created.
        to_reconcile = []
        line_ids_create_command_list = []
        aml_to_exchange_diff_vals = {}

        for i, line in enumerate(self.line_ids):
            if line.flag == 'exchange_diff':
                continue

            amount_currency = line.amount_currency
            balance = line.balance
            if line.flag == 'new_aml':
                to_reconcile.append((i, line.source_aml_id.id))
                exchange_diff = self.line_ids \
                    .filtered(lambda x: x.flag == 'exchange_diff' and x.source_aml_id == line.source_aml_id)
                if exchange_diff:
                    aml_to_exchange_diff_vals[i] = {
                        'amount_residual': exchange_diff.balance,
                        'amount_residual_currency': exchange_diff.amount_currency,
                        'analytic_distribution': exchange_diff.analytic_distribution,
                    }
                    # Squash amounts of exchange diff into corresponding new_aml
                    amount_currency += exchange_diff.amount_currency
                    balance += exchange_diff.balance
            line_ids_create_command_list.append(Command.create(line._get_aml_values(
                sequence=i,
                partner_id=partner_to_set.id if line.flag in ('liquidity', 'auto_balance') else line.partner_id.id,
                amount_currency=amount_currency,
                balance=balance,
            )))

        st_line = self.st_line_id
        move = st_line.move_id

        # Update the move.
        move_ctx = move.with_context(
            skip_invoice_sync=True,
            skip_invoice_line_sync=True,
            skip_account_move_synchronization=True,
            force_delete=True,
        )
        move_ctx.write({'line_ids': [Command.clear()] + line_ids_create_command_list})
        if move_ctx.state == 'draft':
            move_ctx.action_post()

        AccountMoveLine = self.env['account.move.line']
        lines = [
            (move_ctx.line_ids.filtered(lambda x: x.sequence == index),
             self.env['account.move.line'].browse(counterpart_aml_id))
            for index, counterpart_aml_id in to_reconcile
        ]

        # Perform the reconciliation.
        self.env['account.move.line'].with_context(no_exchange_difference=True)._reconcile_plan(
            [line + counterpart for line, counterpart in lines])

        # Fill missing partner.
        st_line_ctx = st_line.with_context(skip_account_move_synchronization=True)
        st_line_ctx.partner_id = partner_to_set

        # Create missing partner bank if necessary.
        if st_line.account_number and st_line.partner_id and not st_line.partner_bank_id:
            st_line_ctx.partner_bank_id = st_line._find_or_create_bank_account()

        # Refresh analytic lines.
        move.line_ids.analytic_line_ids.unlink()
        move.line_ids._create_analytic_lines()

        for line in move.line_ids:
            line.compute_secondary_values()
            line.compute_consolidated_values()

