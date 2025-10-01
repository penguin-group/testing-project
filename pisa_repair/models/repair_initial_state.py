from odoo import models, fields, _
from odoo.exceptions import UserError

class RepairInitialState(models.Model):
    _name = 'repair.initial.state'
    _description = 'Repair Initial State'

    name = fields.Char(string="Name", required=True, translate=True)

    repair_order_ids = fields.Many2many(
        'repair.order',
        'repair_order_initial_state_rel',
        'initial_state_id',
        'repair_order_id',
        string="Repair Orders",
    )