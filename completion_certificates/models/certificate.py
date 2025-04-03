from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Certificate(models.Model):
    _name = 'certificate'
    _description = 'Completion Certificate'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Number', required=True, default=lambda self: self.env['ir.sequence'].next_by_code('completion.certificate'))
    ref = fields.Char(string='Reference')
    partner_id = fields.Many2one('res.partner', string='Vendor', related='purchase_order_id.partner_id', store=True)
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', required=True, domain=[('state', '=', 'purchase'), ('use_certificate', '=', True)])
    date = fields.Date(string='Date', required=True)
    total = fields.Float(string='Total', compute='_compute_total', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string='State', default='draft')
    requester_id = fields.Many2one('res.users', string='Requester', default=lambda self: self.env.user, required=True)
    requester_manager_id = fields.Many2one('res.users', string='Requester Manager', compute='_compute_requester_manager_id')
    vendor_bill_id = fields.Many2one(
        'account.move',
        string='Vendor Bill',
        domain="[('move_type', '=', 'in_invoice'), ('invoice_line_ids.purchase_line_id.order_id', '=', purchase_order_id)]"
    )
    line_ids = fields.One2many('certificate.line', 'certificate_id', string='Lines')
    notes = fields.Text(string='Notes')

    @api.depends('purchase_order_id', 'line_ids.price_subtotal')
    def _compute_total(self):
        for record in self:
            record.total = sum(line.price_subtotal for line in record.line_ids)

    @api.onchange("requester_id")
    def _compute_requester_manager_id(self):
        for certificate in self:
            certificate.requester_manager_id = certificate.requester_id.employee_id.parent_id.user_id
    
    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
            if not record.vendor_bill_id:
                for line in record.line_ids:
                    line.purchase_line_id.qty_received += line.qty_received
                invoices = record.purchase_order_id.action_create_invoice()
                record.vendor_bill_id = invoices['res_id']
                return invoices

    @api.onchange('purchase_order_id')
    def _onchange_purchase_order_id(self):
        self.line_ids = [(5,)]
        if self.purchase_order_id:
            lines = []
            for line in self.purchase_order_id.order_line:
                lines.append((0, 0, {
                    'certificate_id': self.id,
                    'purchase_line_id': line.id,
                    'description': line.name,
                    'qty': line.product_qty,
                    'qty_received': 0,
                    'price_unit': line.price_unit,
                    'tax_ids': [(6, 0, line.taxes_id.ids)],
                    
                }))
            self.line_ids = lines