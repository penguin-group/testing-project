from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CertificateLine(models.Model):
    _name = 'certificate.line'
    _description = 'Certificate Line'

    certificate_id = fields.Many2one('certificate', string='Certificate')
    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line'
    )
    product_id = fields.Many2one('product.product', string='Product', related='purchase_line_id.product_id', readonly=True)
    description = fields.Char(string='Description', default=lambda self: self.purchase_line_id.name) 
    qty = fields.Float(string='Ordered Quantity', related='purchase_line_id.product_qty', readonly=True)
    qty_processed = fields.Float(string='Processed Quantity', compute='_compute_qty_processed', store=True)
    qty_received = fields.Float(string='Received Quantity')
    price_unit = fields.Float(string='Unit Price', compute='_compute_price_unit')
    tax_ids = fields.Many2many('account.tax', string='Taxes', related='purchase_line_id.taxes_id', readonly=True)
    price_subtotal = fields.Float(string='Subtotal')
    date_received = fields.Date(string='Date Received')

    @api.onchange('price_subtotal')
    def _onchange_price_subtotal_update_qty_received(self):
        for line in self:
            if line.price_unit and line.price_subtotal is not None:
                line.qty_received = line.price_subtotal / line.price_unit if line.price_unit != 0 else 0.0

    _sql_constraints = [
        ('unique_purchase_line', 'unique(certificate_id, purchase_line_id)', 'You cannot select the same purchase order line twice.')
    ]

    @api.onchange('purchase_line_id')
    @api.depends('certificate_id.state')
    def _compute_qty_processed(self):
        for line in self:
            confirmed_lines = self.search([
                ('purchase_line_id', '=', line.purchase_line_id.id),
                ('certificate_id.state', '=', 'confirmed')
            ])
            line.qty_processed = sum(confirmed_lines.mapped('qty_received'))
            
    @api.onchange('price_unit', 'qty_received')
    def _compute_price_subtotal(self):
        for line in self:
            line.price_subtotal = line.price_unit * line.qty_received

    @api.constrains('purchase_line_id')
    def _check_purchase_method(self):
        for line in self:
            if line.purchase_line_id.product_id.purchase_method != 'receive':
                raise ValidationError(_('The Control Policy of the product must be "Receive" to create a certificate line.'))
    
    @api.depends('purchase_line_id')
    def _compute_price_unit(self):
        for line in self:
            line.price_unit = line.purchase_line_id.price_unit

