from odoo import models, fields, api
import re
from odoo.exceptions import ValidationError

class Stamping(models.Model):
    _name = 'stamping'
    _description = 'Stamping'

    name = fields.Char('Stamping Number', required=True)
    authorization_number = fields.Char('Authorization Number')
    document_type = fields.Selection(
        string="Document Type", 
        selection=[
            ('out_invoice', 'Invoice'), 
            ('out_refund', 'Credit Note'), 
            ('delivery_note', 'Delivery Note')
        ], 
        default="out_invoice"
    )
    start_date = fields.Date(
        string='Start Date', 
        default=fields.Date.today(), 
        required=True
    )
    end_date = fields.Date(
        string='End Date', 
        required=True
    )
    establishment_number = fields.Char('Establishment Number', required=True)
    expedition_point_number = fields.Char('Expedition Point Number', required=True)
    initial_range = fields.Integer('Initial Invoice Number', required=True)
    final_range = fields.Integer('Final Invoice Number', required=True)
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company
    )

    def validate_stamping_format(self, name):
        pattern = re.compile(r'(^\d{8}$){1}')
        match = pattern.match(name)
        if match is None:
            raise ValidationError('The stamping number does not have the correct format (8 digits)')

    def create(self, vals):
        # Validate the stamping format before creating the record
        if 'name' in vals:
            self.validate_stamping_format(vals['name'])
        rec = super(Stamping, self).create(vals)
        return rec

    def write(self, vals):
        # Validate the stamping format before updating the record
        if 'name' in vals:
            self.validate_stamping_format(vals['name'])
        res = super(Stamping, self).write(vals)
        return res



    