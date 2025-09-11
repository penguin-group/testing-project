from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Company(models.Model):
    _inherit = "res.company"

    github_organization = fields.Char(
        string="GitHub Organization",
        help="The GitHub organization associated with this company.",
    )
    github_token = fields.Char('Github Token')
