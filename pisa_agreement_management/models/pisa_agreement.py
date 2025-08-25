from odoo import models, api, fields


class PisaAgreement(models.Model):
    _name = 'pisa.agreement'

    name = fields.Char(string="Agreement Name", required=True)