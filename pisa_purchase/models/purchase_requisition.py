from odoo import fields, models, _


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    def action_cancel_with_confirmation(self):
        """Wizard to double-check before cancelling a Purchase Requisition."""
        self.ensure_one()

        return {
            'name': _('Double-check before cancelling'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.requisition.cancel.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('pisa_purchase.view_purchase_requisition_cancel_wizard_form').id,
            'target': 'new',
            'context': {'default_purchase_requisition_id': self.id},
        }