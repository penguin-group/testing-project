from odoo import models, fields, api, _

class PurchaseCertificate(models.Model):
    _name = 'purchase.certificate'
    _description = 'Purchase Certificate'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    certificate_file = fields.Binary(string='Certificate', attachment=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('approved', 'Approved'),
    ], string='State', readonly=True, tracking=True, default='draft')

    def action_confirm(self):
        self.ensure_one()
        self.write({'state': 'approved'})
