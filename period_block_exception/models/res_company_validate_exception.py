from datetime import datetime
from odoo import models, _
from odoo.exceptions import RedirectWarning

VALIDATE_EXCEPTION_COMPANY_IDS = (1, 2)
VALIDATE_EXCEPTION_YEARS = (2022, 2023)
VALIDATE_EXCEPTION_YEAR_START_DATETIME = datetime(year=2024, month=1, day=1)

class ResCompanyValidateException(models.Model):

    _inherit = "res.company"
    
    def _validate_fiscalyear_lock(self, values):
        """ Overrides _validate_fiscalyear_lock to add year exception to PISA and PASA companies
            for 2022-2023
        """

        if values.get('fiscalyear_lock_date'):

            company_id = self.env.company.id

            # This expression check if the company is a valid company to make the exception and
            # if the year is the correct
            valid_exception = (
                company_id in VALIDATE_EXCEPTION_COMPANY_IDS and \
                values['fiscalyear_lock_date'].year in VALIDATE_EXCEPTION_YEARS
            )

            # If is VALIDATE_EXCEPTION_COMPANY_IDS only need to check register with date greater than 2024-01-01
            if company_id in VALIDATE_EXCEPTION_COMPANY_IDS:
                draft_entries = self.env['account.move'].search([
                    ('company_id', 'in', self.ids),
                    ('state', '=', 'draft'),
                    ('date', '>=', VALIDATE_EXCEPTION_YEAR_START_DATETIME),
                    ('date', '<=', values['fiscalyear_lock_date'])])
            else:
                draft_entries = self.env['account.move'].search([
                    ('company_id', 'in', self.ids),
                    ('state', '=', 'draft'),
                    ('date', '<=', values['fiscalyear_lock_date'])])
            
            if draft_entries and not valid_exception:
                error_msg = _('There are still unposted entries in the period you want to lock. You should either post or delete them.')
                action_error = {
                    'view_mode': 'tree',
                    'name': _('Unposted Entries'),
                    'res_model': 'account.move',
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', draft_entries.ids)],
                    'search_view_id': [self.env.ref('account.view_account_move_filter').id, 'search'],
                    'views': [[self.env.ref('account.view_move_tree').id, 'list'], [self.env.ref('account.view_move_form').id, 'form']],
                }
                raise RedirectWarning(error_msg, action_error, _('Show unposted entries'))

            if company_id in VALIDATE_EXCEPTION_COMPANY_IDS:
                unreconciled_statement_lines = self.env['account.bank.statement.line'].search([
                    ('company_id', 'in', self.ids),
                    ('is_reconciled', '=', False),
                    ('date', '>=', VALIDATE_EXCEPTION_YEAR_START_DATETIME),
                    ('date', '<=', values['fiscalyear_lock_date']),
                    ('move_id.state', 'in', ('draft', 'posted')),
                ])
            else:
                unreconciled_statement_lines = self.env['account.bank.statement.line'].search([
                    ('company_id', 'in', self.ids),
                    ('is_reconciled', '=', False),
                    ('date', '<=', values['fiscalyear_lock_date']),
                    ('move_id.state', 'in', ('draft', 'posted')),
                ])

            if unreconciled_statement_lines and not valid_exception:
                error_msg = _("There are still unreconciled bank statement lines in the period you want to lock."
                            "You should either reconcile or delete them.")
                action_error = self._get_fiscalyear_lock_statement_lines_redirect_action(unreconciled_statement_lines)
                raise RedirectWarning(error_msg, action_error, _('Show Unreconciled Bank Statement Line'))