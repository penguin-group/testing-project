from odoo import api, fields, models, _
from odoo.tools import index_exists
from odoo.exceptions import ValidationError
import hashlib
import qrcode
from io import BytesIO
import base64
import re
import math


class AccountMove(models.Model):
    _inherit = 'account.move'

    supplier_invoice_authorization_id = fields.Many2one(
        'invoice.authorization',
        string='Supplier Invoice Authorization',
        domain="[('document_type', 'in', ['in_invoice', 'in_refund'])]"
    )
    qr_code = fields.Binary(string="QR Code", compute="generate_qr_code")
    delivery_note_number = fields.Char(string="Delivery Note Number")
    related_invoice_number = fields.Char(string="Related Invoice Number")

    def validate_invoice_authorization(self):
        if self.move_type in ['out_invoice', 'out_refund'] and self.name and self.name != '/':
            inv_auth = self.journal_id.invoice_authorization_id
            if inv_auth:
                number = int(self.name.split('-')[-1])
                establishment_number = self.name.split('-')[0]
                expedition_point_number = self.name.split('-')[1]
                if expedition_point_number != inv_auth.expedition_point_number:
                    raise ValidationError(
                        _('The expedition point number does not match the active invoice authorization.')
                    )
                if establishment_number != inv_auth.establishment_number:
                    raise ValidationError(
                        _('The establishment number does not match the active invoice authorization.')
                    )
                if number > inv_auth.final_invoice_number:
                    raise ValidationError(
                        _('The active invoice authorization has reached its invoice final number.')
                    )
                date = self.invoice_date or fields.Date.today()
                if date > inv_auth.end_date:
                    raise ValidationError(
                        _('The invoice date cannot be later than the invoice authorization’s end date.')
                    )
                if date < inv_auth.start_date:
                    raise ValidationError(
                        _('The invoice date cannot be earlier than the invoice authorization’s start date.')
                    )
                return
            else:
                raise ValidationError(
                    _('There is no invoice authorization.')
                )
        else:
            return

    def validate_empty_vat(self):
        for record in self:
            if not record.partner_id.vat:
                raise ValidationError(_("The customer does not have an assigned VAT. Please add it."))
        return

    @api.onchange('invoice_line_ids')
    @api.depends('invoice_line_ids', 'journal_id')
    def validate_line_count(self):
        for record in self:
            if record.journal_id.max_lines != 0:
                if len(record.invoice_line_ids) > record.journal_id.max_lines:
                    raise ValidationError(
                        _("The maximum number of lines supported in the invoice has been reached."))
        return

    def validate_supplier_invoice_number(self):
        pattern = re.compile(r'^(\d{3}-){2}\d{7}$')
        if not pattern.match(self.ref):
            raise ValidationError(
                _('The invoice number does not have the correct format (xxx-xxx-xxxxxxx)')
            )

    def generate_token(self):
        secret_phrase = str(self.id) + "amakakeruriunohirameki"
        return hashlib.sha256(secret_phrase.encode('utf-8')).hexdigest()
    
    def generate_qr_code(self):
        for record in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            route = f"/invoice/check?invoice_id={record.id}&token={record.generate_token()}"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(f"{base_url}{route}")
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            record.qr_code = qr_image

    def format_self_printer_line(self, line=False):
        """Format the line for self-printer to fit a character limit."""
        limit = 50
        if not line:
            return False
        else:
            limited_lines = []
            current_line = ''
            count = 0
            for char in line:
                count += 1
                current_line += char
                if count == limit:
                    limited_lines.append(current_line)
                    current_line = ''
                    count = 0
            if current_line:
                limited_lines.append(current_line)
            return limited_lines

    def format_amount(self, amount, currency=False, lang=False):
        if not amount:
            amount = 0
        if not lang:
            lang_str = self._context.get('lang')
        else:
            lang_str = lang
        if not currency:
            currency_id = self.env.company.currency_id
        else:
            currency_id = currency

        lang_id = self.env['res.lang'].search([('code', '=', lang_str)], limit=1)

        if lang_id and currency_id:
            fmt = f"%.{currency_id.decimal_places}f"
            return lang_id.format(fmt, amount, grouping=True)
        else:
            return f'{amount:.6f}'

    def amount_to_text(self, amount, currency):
        words = currency.with_context(lang=self.partner_id.lang or 'es_ES').amount_to_text(amount).upper()
        return words

    def action_post(self):
        for record in self:
            if record.move_type in ['in_invoice', 'in_refund']:
                record.validate_supplier_invoice_number()
        result = super(AccountMove, self).action_post()
        for record in self:
            if record.move_type in ['out_invoice', 'out_refund']:
                record.validate_empty_vat()
                record.validate_invoice_authorization()
                record.validate_line_count()
        return result

    def action_invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can more easily see the next step of the workflow. """
        if any(not move.is_invoice(include_receipts=True) for move in self):
            raise UserError(_("Only invoices can be printed"))
        self.filtered(lambda inv: not inv.action_invoice_sent).write({'mark_invoice_as_sent': True})
        return self.env.ref('l10n_py.invoice_report_action').report_action(self)

