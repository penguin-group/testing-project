from odoo import models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_id', 'product_id.type', 'order_id.use_certificate')
    def _compute_qty_received_method(self):
        super(PurchaseOrderLine, self)._compute_qty_received_method()
        for line in self:
            if line.order_id.use_certificate:
                line.qty_received_method = False
                