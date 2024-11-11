from odoo import models, fields, api, _

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu' 

    show = fields.Boolean(string='Show Menu Item', default=True)