from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model_create_multi
    def create(self, vals_list):
        record = super(AccountPayment, self).create(vals_list)
        if 'message_main_attachment_id' in vals_list:
            self._on_attachment_added(record)
        return record

    def write(self, vals):
        res = super(AccountPayment, self).write(vals)
        if 'message_main_attachment_id' in vals:
            self._on_attachment_added(self)
        return res

    def _on_attachment_added(self, record):
        purchase_orders = record.reconciled_bill_ids.line_ids.purchase_line_id.order_id    
        for order in purchase_orders:
            order.message_post(body=_("Attachment added to payment: %s") % record.name, attachment_ids=record.attachment_ids.ids)