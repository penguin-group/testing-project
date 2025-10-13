from odoo import models, fields, api, _

class PurchaseRequestCancelWizard(models.TransientModel):
    _name = 'purchase.request.cancel.wizard'
    _description = 'Purchase Request Cancel Confirmation Wizard'

    purchase_request_id = fields.Many2one('purchase.request', string="Purchase Request", readonly=True)

    def action_confirm_cancel(self):
        """Calls the original method if the user chose to cancel the purchase request."""
        self.ensure_one()

        if 'cancelling_from_reset_button' in self._context:
            self.purchase_request_id.button_draft()
        else:
            self.purchase_request_id.button_rejected()

        return {'type': 'ir.actions.act_window_close'}
