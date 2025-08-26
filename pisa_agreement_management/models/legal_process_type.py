from odoo import models, api, fields


class LegalProcessType(models.Model):
    _name = 'legal.process.type'

    name = fields.Char(string='Legal Process Type', required=True)