from odoo import models, fields, api, _
import re
from odoo.exceptions import ValidationError

class InvoiceAuthorization(models.Model):
    _name = 'invoice.authorization'
    _description = 'Invoice Authorization'

    name = fields.Char('Authorization Number', required=True)
    document_type = fields.Selection(
        string="Document Type", 
        selection=[
            ('out_invoice', 'Customer Invoice'), 
            ('in_invoice', 'Supplier Invoice'),
            ('out_refund', 'Customer Credit Note'), 
            ('in_refund', 'Supplier Credit Note'), 
            ('delivery_note', 'Delivery Note')
        ], 
        default="out_invoice"
    )
    partner_id = fields.Many2one(comodel_name='res.partner', string='Supplier')
    start_date = fields.Date(
        string='Start Date', 
        default=fields.Date.today(), 
        required=True
    )
    end_date = fields.Date(
        string='End Date', 
        required=True
    )
    establishment_number = fields.Char('Establishment Number', required=True, default="001")
    expedition_point_number = fields.Char('Expedition Point Number', required=True, default="001")
    initial_invoice_number = fields.Integer('Initial Invoice Number', required=True, default=1)
    final_invoice_number = fields.Integer('Final Invoice Number', required=True, default=9999999)
    self_printer_authorization = fields.Char('Self-printer Authorization Number')
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company
    )

    def validate_authorization_format(self, name):
        pattern = re.compile(r'(^\d{8}$){1}')
        match = pattern.match(name)
        if match is None:
            raise ValidationError(_('The invoice authorization number does not have the correct format (8 digits)'))

    def create(self, vals):
        # Validate the invoice authorization format before creating the record
        if 'name' in vals:
            self.validate_authorization_format(vals['name'])
        rec = super(InvoiceAuthorization, self).create(vals)
        return rec

    def write(self, vals):
        # Validate the invoice authorization format before updating the record
        if 'name' in vals:
            self.validate_authorization_format(vals['name'])
        res = super(InvoiceAuthorization, self).write(vals)
        return res


