from odoo import models, fields


class AgreementTag(models.Model):
    _name = 'agreement.tag'
    _description = 'Agreement Tags'

    name = fields.Char(string="Agreement Tag", required=True)
    active = fields.Boolean(default=True)
    agreement_id = fields.Many2one("agreement", string="Related Agreement")