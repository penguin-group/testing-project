from odoo import models, api, _
from odoo.exceptions import UserError


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = 'purchase.request.line.make.purchase.order'

    def make_purchase_order(self):
        purchase_order_view = super(PurchaseRequestLineMakePurchaseOrder, self).make_purchase_order()
        purchase_id = purchase_order_view['domain'][0][-1][0]
        purchase_order = self.env['purchase.order'].browse(purchase_id)
        
        # Link attachments from the purchase request to the created purchase order
        request_id = self.item_ids[0].request_id
        request_id._link_attachments_to_purchase_order(purchase_order)

        # Set the unit price based on the estimated cost from the purchase request line
        purchase_order.order_line._get_request_line_estimated_cost()

        return purchase_order_view
    
    @api.model
    def _prepare_purchase_order(self, picking_type, group_id, company, origin):
        data = super(PurchaseRequestLineMakePurchaseOrder, self)._prepare_purchase_order(picking_type, group_id, company, origin)
        project_id = self.item_ids[0].request_id.project_id
        data['project_id'] = project_id.id if project_id else False
        data['user_id'] = data['assignee_id'] = self.item_ids[0].request_id.requested_by.id
        return data

    @api.model
    def _get_and_check_valid_request_line(self, request_line_ids):
        """ This method does the same as the original _check_valid_request_line but instead of raising an error when a line is already done,
            it just removes it from the list of lines to process.
        """
        picking_type = False
        company_id = False

        for line in self.env["purchase.request.line"].browse(request_line_ids):
            
            # Skip lines that are already done
            if line.purchase_state == "done":
                request_line_ids.remove(line.id)
                continue

            if line.request_id.state == "done":
                raise UserError(_("The purchase has already been completed."))
            if line.request_id.state != "approved":
                raise UserError(
                    _("Purchase Request %s is not approved") % line.request_id.name
                )

            line_company_id = line.company_id and line.company_id.id or False
            if company_id is not False and line_company_id != company_id:
                raise UserError(_("You have to select lines from the same company."))
            else:
                company_id = line_company_id

            line_picking_type = line.request_id.picking_type_id or False
            if not line_picking_type:
                raise UserError(_("You have to enter a Picking Type."))
            if picking_type is not False and line_picking_type != picking_type:
                raise UserError(
                    _("You have to select lines from the same Picking Type.")
                )
            else:
                picking_type = line_picking_type

        return request_line_ids

    @api.model
    def get_items(self, request_line_ids):
        """ Full override of this method to call the new method _get_and_check_valid_request_line instead of _check_valid_request_line
        """
        request_line_obj = self.env["purchase.request.line"]
        items = []
        request_line_ids = self._get_and_check_valid_request_line(request_line_ids)
        request_lines = request_line_obj.browse(request_line_ids)
        self.check_group(request_lines)
        for line in request_lines:
            items.append([0, 0, self._prepare_item(line)])
        return items
