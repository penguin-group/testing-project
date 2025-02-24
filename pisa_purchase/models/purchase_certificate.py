from odoo import models, fields, api, _

class PurchaseCertificate(models.Model, models.AbstractModel):
    _name = 'purchase.certificate'
    _description = 'Purchase Certificate'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    certificate_file = fields.Binary(string='Certificate', attachment=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('approved', 'Approved'),
    ], string='State', readonly=True, tracking=True, default='draft')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    def action_confirm(self):
        self.ensure_one()
        self.write({'state': 'approved'})

    def write(self, vals):
        if 'certificate_file' in vals:
            self.message_post(body="Certificate file has been updated.")
        return super(PurchaseCertificate, self).write(vals)
