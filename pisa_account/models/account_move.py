from odoo import fields, models, _, api
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

    company_secondary_currency_name = fields.Char(
        related='company_id.sec_currency_id.name', readonly=True,
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
    
    def action_post(self):
        for record in self:
            # Check invoice confirmation permission
            if record.is_invoice and not record.env.user.has_group('account.group_account_invoice'):
                raise ValidationError(_("You don't have permission to approve an invoice."))
            if record.move_type == 'in_invoice':
                # Check if the "ref" field is blank
                if not record.ref:
                    raise ValidationError(_('The "Invoice Number" field is required.'))
                # Check if the total invoice amount is less than or equal to zero
                if record.amount_total <= 0:
                    raise ValidationError(_('The total invoice amount cannot be zero or negative.'))
                # Is not in group Sr Finance
                if record.env.user.has_group('pisa_account.group_account_sr_finance'):
                    raise ValidationError(_("You don't have permission to approve this invoice."))

        return super(AccountMove, self).action_post()

    def edit_secondary_currency_rate(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'edit.secondary.currency.rate',
            'view_mode': 'form',         
            'view_id': self.env.ref('pisa_account.edit_secondary_currency_rate_view_form').id,      
            'target': 'new',
            'context': {'active_id': self.id}
        }

    def is_inbound(self, include_receipts=True):
        # Override this method to include inbound payments entries
        result = super(AccountMove, self).is_inbound(include_receipts=include_receipts)
        inbound_payment = self.origin_payment_id and self.origin_payment_id.payment_type == 'inbound'
        return any([result, inbound_payment])
    
    @api.depends('currency_id', 'company_secondary_currency_id', 'company_id', 'invoice_date')
    def _compute_invoice_secondary_currency_rate(self):
        if self.company_secondary_currency_id and self.company_id.country_code == "PY":
            for move in self:
                if move.currency_id != move.company_secondary_currency_id:
                    rate_type = 'buy' if move.is_inbound() else 'sell'
                    move.invoice_secondary_currency_rate = self.env['res.currency']._get_conversion_rate(
                        from_currency=move.company_secondary_currency_id,
                        to_currency=move.currency_id,
                        company=move.company_id,
                        date=move.invoice_date or fields.Date.context_today(move),
                        rate_type=rate_type,
                    )
                else:
                    move.invoice_secondary_currency_rate = 1
        else:
            super(AccountMove, self)._compute_invoice_secondary_currency_rate()

    def _compute_fields_for_py_reports(self):
        # Override computation to reflect the amounts according to secondary balance
        company = self.env.company
        if company.sec_currency_id and company.sec_currency_id.name == "PYG" and company.country_code == "PY":
            for record in self:
                if record.move_type == "in_invoice" and record.import_clearance:
                    # Handle import clearance invoices
                    record.amount_vat10 = abs(sum(record.line_ids.filtered(lambda l: l.display_type =='product' and l.account_id.vat_import and 0 in l.tax_ids.mapped('amount')).mapped("secondary_balance")))
                    record.amount_base10 = record.amount_vat10 * 10
                    record.amount_base5 = 0
                    record.amount_vat5 = 0
                    record.amount_exempt = 0
                    record.amount_taxable_imports = record.amount_base10
                else:
                    record.amount_base10 = abs(sum(record.line_ids.filtered(lambda l: l.display_type =='product' and 10 in l.tax_ids.mapped('amount')).mapped("secondary_balance")))
                    record.amount_vat10 = abs(sum(record.line_ids.filtered(lambda l: l.display_type =='tax' and l.tax_line_id and l.tax_line_id.amount == 10).mapped("secondary_balance")))
                    record.amount_base5 = abs(sum(record.line_ids.filtered(lambda l: l.display_type =='product' and 5 in l.tax_ids.mapped('amount')).mapped("secondary_balance")))
                    record.amount_vat5 = abs(sum(record.line_ids.filtered(lambda l: l.display_type =='tax' and l.tax_line_id and l.tax_line_id.amount == 5).mapped("secondary_balance")))
                    record.amount_exempt = abs(sum(record.line_ids.filtered(lambda l: l.display_type =='product' and (0 in l.tax_ids.mapped('amount') or not l.tax_ids)).mapped("secondary_balance")))
                    record.amount_taxable_imports = 0 
        else:
            super(AccountMove, self)._compute_fields_for_py_reports()