from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_view_purchase_request(self):
        """
        Open the related purchase request form view
        """
        requests = self.order_line.mapped('purchase_request_lines.request_id')
        if len(requests) > 1:
            action = {
                'name': 'Purchase Requests',
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.request',
                'view_mode': 'list,form',
                'domain': [('id', 'in', requests.ids)],
            }
        else:
            action = {
                'name': 'Purchase Request',
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.request',
                'view_mode': 'form',
                'res_id': requests.id,
            }
            action['views'] = [(self.env.ref('purchase_request.view_purchase_request_form').id, 'form')]
            action['target'] = 'current'
        return action
