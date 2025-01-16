from odoo import models, api
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_is_zero

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def create(self, vals):
        if not vals.get('analytic_distribution'):
            raise ValidationError("You must provide a value for Analytic Distribution on the lines.")
        return super(AccountMoveLine, self).create(vals)

    def write(self, vals):
        if 'analytic_distribution' not in vals and not self.analytic_distribution:
            raise ValidationError("You must provide a value for Analytic Distribution on the lines.")
        return super(AccountMoveLine, self).write(vals)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        if not vals.get('analytic_distribution'):
            raise ValidationError("You must provide a value for Analytic Distribution on the sales lines.")
        return super(SaleOrderLine, self).create(vals)

    def write(self, vals):
        if 'analytic_distribution' not in vals and not self.analytic_distribution:
            raise ValidationError("You must provide a value for Analytic Distribution on the sales lines.")
        return super(SaleOrderLine, self).write(vals)

class SaleOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def create(self, vals):
        if not vals.get('analytic_distribution'):
            raise ValidationError("You must provide a value for Analytic Distribution on the purchase lines.")
        return super(SaleOrderLine, self).create(vals)

    def write(self, vals):
        if 'analytic_distribution' not in vals and not self.analytic_distribution:
            raise ValidationError("You must provide a value for Analytic Distribution on the purchase lines.")
        return super(SaleOrderLine, self).write(vals)