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

    def action_request_technical_review(self):
        self.write({'state': 'technical_review'})

    def action_request_sourcing_strategy(self):
        self.write({'state': 'sourcing_strategy'})

    def button_confirm(self):
        """
        Override the purchace.order original method just to change the previous state to 'sourcing_strategy'
        """
        for order in self:
            if order.state not in ['sourcing_strategy']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True