from odoo import models, fields, api, Command


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    def _create_vendor_bill(self):
        """Create a vendor bill for this expense."""
        self.ensure_one()
        if not self.sheet_id or self.sheet_id.state != 'approve':
            return
        line_ids = [Command.create(self._prepare_move_lines_vals())],
        invoice_vals = {
            'move_type': 'in_invoice',
            'journal_id': self.sheet_id.journal_id.id, # The default value in this field should be the journal set in the expense settings page.
            'partner_id': self.vendor_id.id,
            'currency_id': self.sheet_id.currency_id.id,
            'invoice_date': fields.Date.context_today(self),
            'line_ids': line_ids,
            'attachment_ids': [
                Command.create(attachment.copy_data({'res_model': 'account.move', 'res_id': False, 'raw': attachment.raw})[0])
                for attachment in self.message_main_attachment_id
            ],
        }
        bill = self.env['account.move'].sudo().create(invoice_vals)
        return bill
            
