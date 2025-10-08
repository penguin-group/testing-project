from odoo import fields, models


class AgreementRenewalTerm(models.Model):
    _name = "agreement.renewal.term"
    _description = "Renewal Term"

    name = fields.Char("Name", required=True)
    active = fields.Boolean(default=True)