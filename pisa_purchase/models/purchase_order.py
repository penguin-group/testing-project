from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import groupby
from odoo.tools.float_utils import float_is_zero

class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = "purchase.order"

    def _compute_validation_status(self):
            super(PurchaseOrder, self)._compute_validation_status()
            for order in self:
                if order.requisition_id and order.requisition_id.validation_status == 'validated':
                    order.validation_status = 'validated'

    assignee_id = fields.Many2one('res.users', string='Assignee', help='User responsible for this RFQ',
        default=lambda self: self.env.user.id)
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

    @api.model_create_multi
    def create(self, vals):
        # Validate partner country if being set
        for val in vals:
            if 'partner_id' in val:
                partner = self.env['res.partner'].browse(val['partner_id'])
                if not partner.country_id:
                    raise ValidationError(_("Suppliers must have a country set."))
        
        # Create the PO
        order = super(PurchaseOrder, self).create(vals)
        
        # Subscribe assignee to messages
        self.subscribe_assignee(order)

        # Replicate off_budget value from PR
        if 'active_model' in self._context and self._context['active_model'] == 'purchase.request':
            purchase_req = self.env['purchase.request'].search([('id', '=', self._context['active_id'])])
            order.off_budget = purchase_req.off_budget

        return order
    
    def write(self, vals):
        # Validate partner country if being set
        if 'partner_id' in vals:
            partner = self.env['res.partner'].browse(vals['partner_id'])
            if not partner.country_id:
                raise ValidationError(_("Suppliers must have a country set."))
        
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

    def action_cancel_with_confirmation(self):
        """Wizard to double-check before cancelling a PO."""
        self.ensure_one()

        # If the PO is not in a validated state, cancel directly.
        if self.state not in ('purchase', 'done'):
            return self.button_cancel()

        return {
            'name': _('Double-check before cancelling'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.cancel.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('pisa_purchase.view_purchase_cancel_wizard_form').id,
            'target': 'new',
            'context': {'default_purchase_order_id': self.id},
        }
    def _validate_tier(self, tiers=False):
        super(PurchaseOrder, self)._validate_tier()

        if all(r.status == 'approved' for r in self.review_ids):
            self.state = 'purchase'

    def _prepare_invoice(self):
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()

        # Attach invoice, if any
        if 'uploaded_invoice' in self._context:
            ir_attachment = self.env['ir.attachment'].create({
                'type': 'binary',
                'res_model': "account.move",
                'name': f"Invoice",
                'datas': self._context['uploaded_invoice']
            })
            invoice_vals['attachment_ids'] = [(4, ir_attachment.id)]

        return invoice_vals

    def open_wizard_to_create_bill_with_attachment(self):
        return {
            'name': _('Create Bill with File Attachment'),
            'type': 'ir.actions.act_window',
            'res_model': 'bill.with.file.attachment.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('pisa_purchase.create_bill_with_attachment_wizard').id,
            'target': 'new',
            'context': {'default_purchase_order_id': self.id},
        }
