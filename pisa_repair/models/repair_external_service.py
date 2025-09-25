from odoo import models, fields, _
from odoo.exceptions import UserError

class RepairExternalService(models.Model):
    _name = 'repair.external.service'
    _description = 'Repair External Service'

    name = fields.Char(string="Name", required=True)

    repair_order_ids = fields.One2many(
        'repair.order',
        'external_service_id',
        string="Repair Orders",
    )