# models/invoice_wizard.py
from odoo import models, fields, _

class InvoiceCancel(models.TransientModel):
    _name = 'invoice.cancel'
    _description = 'Invoice Cancellation Wizard'

    reason = fields.Text(string='Reason', required=True)

    def action_apply(self):
        active_id = self._context.get('active_id')
        invoice = self.env['account.move'].browse(active_id)
        # Cancel the invoice
        invoice.cancel_invoice()
        # Log the action
        invoice.message_post(body=_('Cancellation Reason: %s' % self.reason), subject=_("Invoice Cancellation"))
        return {'type': 'ir.actions.act_window_close'}
