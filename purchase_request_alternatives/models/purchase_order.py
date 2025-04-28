from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_request_ids = fields.Many2many(
        'purchase.request',
        string='Purchase Requests',
        compute='_compute_purchase_requests'
    )
    purchase_request_count = fields.Integer(string='Purchase Requests', compute='_compute_purchase_request_count')

    def _compute_purchase_requests(self):
        for rec in self:
            requests = rec.order_line.mapped('purchase_request_lines.request_id')
            requests += rec.alternative_po_ids.order_line.mapped('purchase_request_lines.request_id')
            rec.purchase_request_ids = [(6, 0, list(set(requests.ids)))]
    
    def _compute_purchase_request_count(self):
        for rec in self:
            rec.purchase_request_count = len(rec.purchase_request_ids)
    
    def action_view_purchase_request(self):
        """
        Open the related purchase request form view
        """
        self.ensure_one()
        if len(self.purchase_request_ids) > 1:
            action = {
                'name': 'Purchase Requests',
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.request',
                'view_mode': 'list,form',
                'domain': [('id', 'in', self.purchase_request_ids.ids)],
            }
        else:
            action = {
                'name': 'Purchase Request',
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.request',
                'view_mode': 'form',
                'res_id': self.purchase_request_ids.id,
            }
            action['views'] = [(self.env.ref('purchase_request.view_purchase_request_form').id, 'form')]
            action['target'] = 'current'
        return action
