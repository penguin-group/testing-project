from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    assignee_id = fields.Many2one('res.users', string='Assignee', help='User responsible for this RFQ')
    extra_cost_po_ids = fields.Many2many('purchase.order', 'purchase_extra_cost_rel', 'main_po_id', 'extra_cost_po_id',
        string='Extra Cost POs', help='Link extra cost POs (customs, shipping etc) to this PO for accurate cost tracking')
    off_budget = fields.Boolean(string='Off-Budget', tracking=True)

    def _compute_next_review(self):
        # Override original method to change the next review string
        for rec in self:
            review = rec.review_ids.sorted("sequence").filtered(
                lambda x: x.status == "pending"
            )[:1]
            rec.next_review = review.name if review else ""

    @api.depends('order_line.price_total', 'extra_cost_po_ids.amount_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                line._compute_amount()
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            for extra_cost_po in order.extra_cost_po_ids:
                amount_untaxed += extra_cost_po.amount_untaxed
                amount_tax += extra_cost_po.amount_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.model_create_multi
    def create(self, vals):
        # Create the PO
        order = super(PurchaseOrder, self).create(vals)
        
        # Subscribe assignee to messages
        self.subscribe_assignee(order)

        # Replicate off_budget value from PR
        if self._context['active_model'] == 'purchase.request':
            purchase_req = self.env['purchase.request'].search([('id', '=', self._context['active_id'])])
            order.off_budget = purchase_req.off_budget

        return order
    
    def write(self, vals):
        # Store the old extra cost POs before write
        old_extra_cost_pos = {order.id: order.extra_cost_po_ids for order in self}
        result = super(PurchaseOrder, self).write(vals)
        
        # After write, sync the links
        if 'extra_cost_po_ids' in vals:
            for order in self:
                old_pos = old_extra_cost_pos[order.id]
                order._sync_extra_cost_pos(old_pos)

        # Subscribe assignee to messages
        if 'assignee_id' in vals and vals['assignee_id']:
            for order in self:
                self.subscribe_assignee(order)
        
        return result

    def subscribe_assignee(self, record):
        # Subscribe assignee to messages
        partner_id = record.assignee_id.partner_id
        subscribers = [partner_id.id] if partner_id and partner_id not in record.sudo().message_partner_ids else None
        if subscribers:
            record.message_subscribe(subscribers)

    def _sync_extra_cost_pos(self, old_extra_cost_pos=None):
        """Ensure reciprocal linking between main PO and its extra cost POs.
        When a PO is unlinked, also remove its reciprocal link."""
        current_pos = self.extra_cost_po_ids
        
        # Handle newly added POs - add reciprocal links
        for linked_po in current_pos - (old_extra_cost_pos or self.env['purchase.order']):
            if self not in linked_po.extra_cost_po_ids:
                linked_po.with_context(no_reciprocal=True).write({
                    'extra_cost_po_ids': [(4, self.id)]
                })
        
        # Handle unlinked POs - remove reciprocal links
        for unlinked_po in (old_extra_cost_pos or self.env['purchase.order']) - current_pos:
            if self in unlinked_po.extra_cost_po_ids:
                unlinked_po.with_context(no_reciprocal=True).write({
                    'extra_cost_po_ids': [(3, self.id)]
                })
