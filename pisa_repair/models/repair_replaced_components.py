from odoo import models, fields, _
from odoo.exceptions import UserError

class RepairReplacedComponents(models.Model):
    _name = 'repair.replaced.components'
    _description = 'Replaced Components'

    name = fields.Char(string="Component Name", required=True)

    repair_order_ids = fields.Many2many(
        'repair.order',
        'repair_order_replaced_components_rel',
        'replaced_component_id',
        'repair_order_id',
        string="Repair Orders",
    )