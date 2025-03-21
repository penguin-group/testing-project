from odoo import models, fields, api


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'

    def make_purchase_order(self):
        purchase_order_view = super(PurchaseRequestLineMakePurchaseOrder, self).make_purchase_order()
        purchase_id = purchase_order_view['domain'][0][-1][0]
        purchase_order = self.env['purchase.order'].browse(purchase_id)
        request_id = self.item_ids[0].request_id
        request_id._link_attachments_to_purchase_order(purchase_order)
        return purchase_order_view
