from odoo import fields, models, api


class BillFileAttachmentWizard(models.TransientModel):
    _name = "bill.with.file.attachment.wizard"

    attached_invoice_file = fields.Binary("Upload Invoice", required=True)

    def create_bill_with_attachment(self):
        relevant_po = self.env['purchase.order'].browse(self._context['active_id'])
        relevant_po.with_context(uploaded_invoice=self.attached_invoice_file).action_create_invoice()
