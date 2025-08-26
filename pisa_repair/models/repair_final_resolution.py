from odoo import models, fields, _
from odoo.exceptions import UserError

class RepairFinalResolution(models.Model):
    _name = 'repair.final.resolution'
    _description = 'Final Resolution'

    name = fields.Char(string="Resolution Name", required=True, translate=True)

    repair_order_ids = fields.Many2many(
        'repair.order',
        'repair_order_final_resolution_rel',
        'final_resolution_id',
        'repair_order_id',
        string="Repair Orders",
    )