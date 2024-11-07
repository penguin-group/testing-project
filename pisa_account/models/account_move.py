from odoo import fields, models, _
from odoo.exceptions import ValidationError
import hashlib
import qrcode
from io import BytesIO
import base64
import re
import math


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_info_qr_code = fields.Binary(
        string="Payment Info QR Code", 
        compute="_generate_payment_info_qr_code"
    )

    def _generate_payment_info_qr_code(self):
        for record in self:
            html_content = """
                        {{ payment_info }}
                    """
            html_content = re.sub(
                r'{{ payment_info }}', 
                str(record.journal_id.payment_info).replace('<br>', '\n'), 
                html_content
            )
            html_tags_pattern = re.compile(r'<.*?>')
            plain_text = re.sub(html_tags_pattern, '', html_content)
        
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(plain_text)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            record.payment_info_qr_code = qr_image
    
    # Override validation for supplier invoice number field (ref).
    # It only validates when the journal is for local suppliers of type 2.
    # For other types, it will not consider the invoice number format.
    def validate_supplier_invoice_number(self):
        if self.ref and self.journal_id.local_suppliers:
            super(AccountMove, self).validate_supplier_invoice_number()

    def action_post(self):
        for record in self:
            # Check invoice confirmation permission
            if record.is_invoice and not record.env.user.has_group('pisa_account.group_account_invoice_approver'):
                raise ValidationError(_("You don't have permission to approve an invoice."))
            if record.move_type == 'in_invoice':
                # Check if the "ref" field is blank
                if not record.ref:
                    raise ValidationError(_('The "Invoice Number" field is required.'))
                # Check if the total invoice amount is less than or equal to zero
                if record.amount_total <= 0:
                    raise ValidationError(_('The total invoice amount cannot be zero or negative.'))
        return super(AccountMove, self).action_post()


