from odoo import models, fields, api, _

class PurchaseCancelWizard(models.TransientModel):
    _name = 'purchase.cancel.wizard'
    _description = 'Purchase Order Cancel Confirmation Wizard'

    purchase_order_id = fields.Many2one('purchase.order', string="Purchase Order", readonly=True)

    def action_confirm_cancellation(self):
        """Calls the original cancel method if the user chose to cancel the PO."""
        self.ensure_one()
        self.purchase_order_id.button_cancel()
        return {'type': 'ir.actions.act_window_close'}
