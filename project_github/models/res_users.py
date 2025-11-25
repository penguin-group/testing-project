from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"
    
    github_token = fields.Char('User Github Token')