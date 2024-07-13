from odoo import _, api, fields, models, tools, Command


class BankWidget(models.Model):
    _inherit='bank.rec.widget'

    @api.model
    def js_action_reconcile_st_line(self, st_line_id, params):
        st_line = self.env['account.bank.statement.line'].browse(st_line_id)

        # Remove the existing lines.
        move = st_line.move_id

        # Update the move.
        move_ctx = move.with_context(
            skip_invoice_sync=True,
            skip_invoice_line_sync=True,
            skip_account_move_synchronization=True,
            force_delete=True,
        )
        move_ctx.write({'line_ids': [Command.clear()] + params['command_list']})
        if move_ctx.state == 'draft':
            move_ctx.action_post()

        # Perform the reconciliation.
        for index, counterpart_aml_id in params['to_reconcile']:
            counterpart_aml = self.env['account.move.line'].browse(counterpart_aml_id)
            (move_ctx.line_ids.filtered(lambda x: x.sequence == index) + counterpart_aml).reconcile()

        # Fill missing partner.
        st_line.with_context(skip_account_move_synchronization=True).partner_id = params['partner_id']

        # Create missing partner bank if necessary.
        if st_line.account_number and st_line.partner_id and not st_line.partner_bank_id:
            st_line.partner_bank_id = st_line._find_or_create_bank_account()

        # Refresh analytic lines.
        move.line_ids.analytic_line_ids.unlink()
        move.line_ids._create_analytic_lines()

        for line in move.line_ids:
            line.compute_secondary_values()
            line.compute_consolidated_values()

