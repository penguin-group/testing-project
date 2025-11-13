from odoo import models, fields, api, _

class PurchaseRequisitionCancelWizard(models.TransientModel):
    _name = 'purchase.requisition.cancel.wizard'
    _description = 'Purchase Requisition Cancel Confirmation Wizard'

    purchase_requisition_id = fields.Many2one('purchase.requisition', string="Purchase Requisition", readonly=True)

    def action_confirm_cancellation(self):
        """Calls the original cancel method if the user chose to cancel the purchase requisition."""
        self.ensure_one()
        self.purchase_requisition_id.action_cancel()
        return {'type': 'ir.actions.act_window_close'}
