from odoo import models, api
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_is_zero

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.constrains('analytic_distribution')
    def _check_analytic_distribution(self):
        for line in self:
            if line.move_id.is_invoice(include_receipts=True):
                if line.product_id and line.product_id.requires_analytic_account:
                    if not line.analytic_distribution:
                        raise ValidationError(
                            "The analytic distribution is mandatory for all invoice lines."
                        )


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.constrains('analytic_distribution')
    def _check_analytic_distribution(self):
        for line in self:
                if line.product_id and line.product_id.requires_analytic_account:
                    if not line.analytic_distribution:
                        raise ValidationError(
                            "The analytical distribution is mandatory for all lines."
                        )

class SaleOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.constrains('analytic_distribution')
    def _check_analytic_distribution(self):
        for line in self:
                if line.product_id and line.product_id.requires_analytic_account:
                    if not line.analytic_distribution:
                        raise ValidationError(
                            "The analytical distribution is mandatory for all lines."
                        )