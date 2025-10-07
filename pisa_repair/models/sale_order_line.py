from odoo import models, fields

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    related_quotation_ids = fields.Many2one(
        'sale.order',
        string='Related Quotations',
        help='Original quotations related to this order line.'
    )

    lot_serial = fields.Char(string='Lot/Serial Number')

    repair_id = fields.Many2one('repair.order', string='Repair Order')