from datetime import date
from odoo import fields, models, _
from odoo.exceptions import RedirectWarning, UserError

COMPANIES_TO_VALIDATE = [1, 2]  # Infra & Academy

SOFT_LOCK_DATE_FIELDS = [
    'fiscalyear_lock_date',
    'tax_lock_date',
    'sale_lock_date',
    'purchase_lock_date',
]

LOCK_DATE_FIELDS = [
    *SOFT_LOCK_DATE_FIELDS,
    'hard_lock_date',
]

class ResCompanyValidateException(models.Model):

    _inherit = "res.company"

    def _validate_locks(self, values):
        """Partial override of res.company._validate_locks."""

        if self.env.company.id in COMPANIES_TO_VALIDATE and 'fiscalyear_lock_date' in values:
            """If and only if the user is on PISA or PASA, and if they try to change
             the global lock date, then super() is not called because the original method
            raises an exception that we need to avoid. The condition to raise the
            exception in the original method was finding unreconciled records, and at the time
            of writing this custom logic, our database was having unreconciled entries that we
            wanted to ignore for business purposes. Whether super() was called before or after
            any custom modifications wouldn't matter, as the exception would be raised either way,
            ignoring our business needs.
            - The business requires bypassing warnings for unreconciled records from 2022 and 2023
            made from PISA and PASA. This module itself is a temporary measure.
            """

            new_locks = {field: fields.Date.to_date(values[field])for field in LOCK_DATE_FIELDS if field in values}

            fiscalyear_lock_date = new_locks.get('fiscalyear_lock_date')
            hard_lock_date = new_locks.get('hard_lock_date')
            sale_lock_date = new_locks.get('sale_lock_date')
            purchase_lock_date = new_locks.get('purchase_lock_date')
            fiscal_lock_date = None
            if fiscalyear_lock_date or hard_lock_date:
                fiscal_lock_date = max(fiscalyear_lock_date or date.min, hard_lock_date or date.min)

            # Check for unreconciled bank statement lines
            if fiscal_lock_date:
                unreconciled_statement_lines = self.env['account.bank.statement.line'].search(
                    self._get_unreconciled_statement_lines_domain(fiscal_lock_date)
                )

                if unreconciled_statement_lines:
                    if unreconciled_statement_lines.filtered(lambda l: l.date.year not in (2022, 2023)):
                        error_msg = _("There are still unreconciled bank statement lines in the period you want to lock."
                                      "You should either reconcile or delete them.")
                        action_error = self._get_unreconciled_statement_lines_redirect_action(unreconciled_statement_lines)
                        raise RedirectWarning(error_msg, action_error, _('Show Unreconciled Bank Statement Line'))

        else:
            # Delegate to super() if the main condition resolves to False.
            super(ResCompanyValidateException, self)._validate_locks(values)
