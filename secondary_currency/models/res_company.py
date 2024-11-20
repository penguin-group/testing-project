from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit ='res.company'

    sec_currency_id = fields.Many2one(
        'res.currency', 
        string='Secondary Currency', 
        default=lambda self: self._default_currency_id(), 
        help='Currency used for secondary accounting'
    )