from odoo import models, api
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_is_zero


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.constrains('analytic_distribution')
    def _check_analytic_distribution(self):
        for line in self:
            if line.move_id.is_invoice(include_receipts=True) or line.move_id.move_type == 'entry':
                if not line.analytic_distribution:
                    raise ValidationError(
                        "The analytic distribution is mandatory for all invoice and journal entry lines."
                    )

                # total_distribution = sum(line.analytic_distribution.values())
                # if not float_is_zero(total_distribution - 1.0, precision_digits=2):
                #     raise ValidationError(
                #         "The analytic distribution must sum to 100% for all lines."
                #     )
