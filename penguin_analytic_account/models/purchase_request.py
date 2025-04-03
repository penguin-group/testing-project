from odoo import models, api, _
from odoo.exceptions import ValidationError

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.constrains('line_ids')
    def _check_analytic_account(self):
        for request in self:
            for line in request.line_ids:
                if line.product_id.requires_analytic_account and not line.analytic_distribution:
                    raise ValidationError(_(
                        "The product '%s' requires an analytic account, but none was provided on the line."
                    ) % line.product_id.display_name)