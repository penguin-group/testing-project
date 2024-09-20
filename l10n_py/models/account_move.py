from odoo import api, fields, models, _
from odoo.tools import index_exists
from odoo.exceptions import ValidationError

import re
import math


class AccountMove(models.Model):
    _inherit = 'account.move'

    supplier_invoice_authorization_id = fields.Many2one(
        'invoice.authorization',
        string='Supplier Invoice Authorization',
        domain="[('document_type', 'in', ['in_invoice', 'in_refund'])]"
    )

    def validate_invoice_authorization(self):
        if self.move_type in ['out_invoice', 'out_refund'] and self.name and self.name != '/':
            inv_auth = self.journal_id.invoice_authorization_id
            if inv_auth:
                number = int(self.name.split('-')[-1])
                establishment_number = self.name.split('-')[0]
                expedition_point_number = self.name.split('-')[1]
                if expedition_point_number != inv_auth.expedition_point_number:
                    raise ValidationError(
                        'The expedition point number does not match the active invoice authorization.'
                    )
                if establishment_number != inv_auth.establishment_number:
                    raise ValidationError(
                        'The establishment number does not match the active invoice authorization.'
                    )
                if number > inv_auth.final_range:
                    raise ValidationError(
                        'The active invoice authorization has reached its invoice final number.'
                    )
                date = self.invoice_date or fields.Date.today()
                if date > inv_auth.end_date:
                    raise ValidationError(
                        'The invoice date cannot be later than the invoice authorization’s end date.'
                    )
                if date < inv_auth.start_date:
                    raise ValidationError(
                        'The invoice date cannot be earlier than the invoice authorization’s start date.'
                    )
                return
            else:
                raise ValidationError(
                    'There is no invoice authorization.'
                )
        else:
            return

    def validate_empty_vat(self):
        for record in self:
            if not record.partner_id.vat:
                raise ValidationError("The customer does not have an assigned VAT. Please add it.")
        return

    @api.onchange('invoice_line_ids')
    @api.depends('invoice_line_ids', 'journal_id')
    def validate_line_count(self):
        for record in self:
            if record.journal_id.max_lines != 0:
                if len(record.invoice_line_ids) > record.journal_id.max_lines:
                    raise ValidationError(
                        "The maximum number of lines supported in the invoice has been reached.")
        return

    def validate_supplier_invoice_number(self):
        pattern = re.compile(r'^(\d{3}-){2}\d{7}$')
        if not pattern.match(self.ref):
            raise ValidationError(
                'The invoice number does not have the correct format (xxx-xxx-xxxxxxx)'
            )

    def action_post(self):
        for record in self:
            if record.move_type in ['in_invoice', 'in_refund']:
                validate_supplier_invoice_number()
        result = super(AccountMove, self).action_post()
        for record in self:
            if record.move_type in ['out_invoice', 'out_refund']:
                record.validate_empty_vat()
                record.validate_invoice_authorization()
                record.validate_line_count()
        return result


