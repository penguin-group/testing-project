from odoo import models, fields, _
from odoo.exceptions import ValidationError


class RepairStep(models.Model):
    _name = 'repair.steps'
    _description = 'Steps to be performed'
    _rec_name = 'name'
    _order = 'sequence, id'

    name = fields.Char(string="Steps", required=True, index=True)

    type = fields.Selection([
        ('hydro', 'Hydro'),
        ('fan', 'Fan'),
        ('immersion', 'Immersion'),
        ('general', 'General'),
    ], string='Type', default='general', required=True)

    url = fields.Char(string='URL', required=False, default=None)

    sequence = fields.Integer(string='Sequence', default=10)

    order_rel_ids = fields.One2many(
        'repair.order.steps.rel',
        'step_id',
        string="Orders"
    )