from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    certificate_count = fields.Integer(string='Certificates', compute='_compute_certificate_count')
    use_certificate = fields.Boolean(string='Use Certificate')

    def _compute_certificate_count(self):
        for order in self:
            order.certificate_count = self.env['certificate'].search_count([('purchase_order_id', '=', order.id)])

    def action_view_certificates(self):
        self.ensure_one()
        certificates = self.env['certificate'].search([('purchase_order_id', '=', self.id)])
        if not certificates:
            certificates = self.env['certificate'].create({
                'purchase_order_id': self.id,
                'date': fields.Date.today(),
            })
        action = self.env.ref('completion_certificates.action_certificate').read()[0]
        action['domain'] = [('id', 'in', certificates.ids)]
        return action

    @api.constrains('order_line', 'use_certificate')
    def _check_use_certificate(self):
        for order in self:
            if order.use_certificate and self._not_service_products():
                raise ValidationError(_('Only service products are allowed in the order lines.'))
            if not order.use_certificate and self.certificate_count > 0:
                raise ValidationError(_('There are certificates linked to this order.'))
        
    def _not_service_products(self):
        for order in self:
            return len(order.order_line.filtered(lambda line: line.product_id.type != 'service')) > 0


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_id', 'product_id.type', 'order_id.use_certificate')
    def _compute_qty_received_method(self):
        super(PurchaseOrderLine, self)._compute_qty_received_method()
        for line in self:
            if line.order_id.use_certificate:
                line.qty_received_method = False
