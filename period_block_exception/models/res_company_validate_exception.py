from datetime import datetime
from odoo import models, _
from odoo.exceptions import RedirectWarning

ALLOWED_COMPANY_IDS = (1, 2)
YEARS_TO_BYPASS = (2022, 2023)
CURRENT_STARTING_DATETIME = datetime(year=2025, month=1, day=1)

class ResCompanyValidateException(models.Model):

    _inherit = "res.company"
    
    def _validate_locks(self, values):
        """
        Overrides _validate_locks to bypass warning for unreconciled entries found in 2022 and 2023 records.
        Works exclusively for Penguin Infrastructure and Penguin Academy.
        """
        # res = super(ResCompanyValidateException, self)._validate_locks(values)

        if values.get('fiscalyear_lock_date'):
            company_id = self.env.company.id  # Current Odoo's company environment
            is_correct_company = (company_id in ALLOWED_COMPANY_IDS)

            if not is_correct_company:
                draft_entries = self.env['account.move'].search([
                    ('company_id', 'in', self.ids),
                    ('state', '=', 'draft'),
                    ('date', '<=', values['fiscalyear_lock_date'])])

                if draft_entries:
                    error_msg = _('There are still unposted entries in the period you want to lock. You should either post or delete them.')
                    action_error = {
                        'view_mode': 'list',
                        'name': _('Unposted Entries'),
                        'res_model': 'account.move',
                        'type': 'ir.actions.act_window',
                        'domain': [('id', 'in', draft_entries.ids)],
                        'search_view_id': [self.env.ref('account.view_account_move_filter').id, 'search'],
                        'views': [[self.env.ref('account.view_move_tree').id, 'list'], [self.env.ref('account.view_move_form').id, 'form']],
                    }
                    raise RedirectWarning(error_msg, action_error, _('Show unposted entries'))

            if not is_correct_company:
                unreconciled_statement_lines = self.env['account.bank.statement.line'].search(
                    self._get_unreconciled_statement_lines_domain(values.get('fiscalyear_lock_date'))
                )

                if unreconciled_statement_lines:
                    error_msg = _("There are still unreconciled bank statement lines in the period you want to lock."
                                "You should either reconcile or delete them.")
                    action_error = self._get_fiscalyear_lock_statement_lines_redirect_action(unreconciled_statement_lines)
                    raise RedirectWarning(error_msg, action_error, _('Show Unreconciled Bank Statement Line'))