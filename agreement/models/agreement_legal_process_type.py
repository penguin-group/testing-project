from odoo import models, api, fields


class AgreementLegalProcessType(models.Model):
    _name = 'agreement.legal.process.type'

    name = fields.Char(string='Legal Process Type', required=True)
    active = fields.Boolean(default=True)