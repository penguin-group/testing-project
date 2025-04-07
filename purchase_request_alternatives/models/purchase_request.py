from odoo import models, api

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    @api.depends("line_ids")
    def _compute_purchase_count(self):
        # Replace original method to add alternatives to the purchase count
        for rec in self:
            purchase_orders = rec.mapped("line_ids.purchase_lines.order_id") + rec.mapped("line_ids.purchase_lines.order_id.alternative_po_ids")
            purchase_orders = self.env['purchase.order'].browse(list(set(purchase_orders.ids)))
            rec.purchase_count = len(purchase_orders)

    def action_view_purchase_order(self):
        # Replace original method to add alternatives to the purchase list
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_rfq")
        lines = self.mapped("line_ids.purchase_lines.order_id") + self.mapped("line_ids.purchase_lines.order_id.alternative_po_ids")
        if len(lines) > 1:
            action["domain"] = [("id", "in", list(set(lines.ids)))]
        elif lines:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = lines.id
        return action