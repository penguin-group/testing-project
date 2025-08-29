from odoo import models, api, fields


class AgreementType(models.Model):
    _name = 'agreement.type'

    name = fields.Char(string='Type Name', required=True)