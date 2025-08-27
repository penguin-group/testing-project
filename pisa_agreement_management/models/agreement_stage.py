from odoo import models, fields, api


class AgreementStage(models.Model):
    _name = 'agreement.stage'
    _description = 'Agreement Stage'
    _order = 'sequence'

    active = fields.Boolean('Active', default=True)
    name = fields.Char(string='Name', required=True, translate=True)
    fold = fields.Boolean('Folded in Kanban', default=False)
    sequence = fields.Integer(string='Sequence', default=50)