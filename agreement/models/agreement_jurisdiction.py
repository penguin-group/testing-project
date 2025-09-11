from odoo import fields, models


class AgreementJurisdiction(models.Model):
    _name = "agreement.jurisdiction"
    _description = "Jurisdiction"

    name = fields.Char("Name", required=True)
    active = fields.Boolean(default=True)