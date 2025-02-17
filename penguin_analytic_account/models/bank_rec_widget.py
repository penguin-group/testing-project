from odoo import models, _
from odoo.exceptions import ValidationError

class BankRecWidget(models.Model):
    _inherit = "bank.rec.widget"

    def _validation_lines_vals(self, line_ids_create_command_list, aml_to_exchange_diff_vals, to_reconcile):
        super(BankRecWidget, self)._validation_lines_vals(line_ids_create_command_list, aml_to_exchange_diff_vals, to_reconcile)
        for line in self.line_ids:
            if line.flag != 'new_aml':
                continue
            if not line['analytic_distribution']:
                raise ValidationError(_("The analytic distribution of the bank reconciliation line cannot be empty."))


    