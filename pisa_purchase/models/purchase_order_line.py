from odoo import models, fields, api, _


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_request_line_estimated_cost(self):
        for line in self:
            line.price_unit = self.purchase_request_lines.estimated_cost or 0.0
