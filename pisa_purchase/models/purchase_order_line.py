from odoo import models, fields, api, _


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_request_line_estimated_cost(self):
        for line in self:
            if line.purchase_request_lines:
                # Calculate weighted average estimated cost based on quantities
                total_cost = 0.0
                total_qty = 0.0
                
                for request_line in line.purchase_request_lines:
                    if hasattr(request_line, 'estimated_cost') and request_line.estimated_cost:
                        qty = request_line.product_qty or 1.0
                        total_cost += request_line.estimated_cost * qty
                        total_qty += qty
                
                if total_qty > 0:
                    line.price_unit = total_cost / total_qty
                else:
                    # Fallback to first available estimated cost
                    line.price_unit = line.purchase_request_lines[0].estimated_cost or 0.0
