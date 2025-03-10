from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    assignee_id = fields.Many2one('res.users', string='Assignee', help='User responsible for this RFQ')
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('technical_review', 'Technical Review'),
        ('sourcing_strategy', 'Sourcing Strategy'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
