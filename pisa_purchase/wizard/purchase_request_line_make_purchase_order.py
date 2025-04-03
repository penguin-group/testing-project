from odoo import models, fields, api, _


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'

    @api.model
    def _prepare_purchase_order(self, picking_type, group_id, company, origin):
        data = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_purchase_order(picking_type, group_id, company, origin)
        project_id = self.item_ids[0].request_id.project_id
        data['project_id'] = project_id.id if project_id else False
        data['user_id'] = self.item_ids[0].request_id.requested_by.id
        return data