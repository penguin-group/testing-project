from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    requires_analytic_account = fields.Boolean(string='Requires Analytic Account', default=True)

    