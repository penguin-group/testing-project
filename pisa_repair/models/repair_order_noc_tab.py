from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class RepairOrderFields(models.Model):
    _inherit = 'repair.order'

    diagnosed_failure = fields.Many2one(
        'repair.fault',
        string='Diagnosed Failure',
        required=True,
        ondelete='restrict',
    )

    origin_location = fields.Many2one(
        'stock.location',
        string='Origin Location',
        readonly=True
    )

    destination_location = fields.Many2one(
        'stock.location',
        string='Destination Location',
        domain="[('usage','=','internal'), ('barcode', 'in', ['LABSTOCK', 'LAB_2STOCK', 'ESLSTOCK', 'ONRSTOCK', 'WRHSTOCK'])]", 
        required=True
    )

    show_external_service = fields.Boolean(
        compute="_compute_show_external_service",
        store=False
    )

    @api.onchange('destination_location')
    def _compute_show_external_service(self):
        for record in self:
            if record.destination_location and record.destination_location.warehouse_id == self.env.ref('pisa_inventory.warehouse_external'):
                record.show_external_service = True
            else:
                record.show_external_service = False

    @api.model
    def create(self, vals):
        record = super(RepairOrderFields, self).create(vals)

        if record.lot_id:
            record.write({'origin_location': record.lot_id.location_id.id})

        return record

    def _handle_location_transfer(self, record, new_state, previous_state):
        if record.extraction:
            if new_state == 'under_repair' and record.destination_location:
                record.lot_id.location_id = record.destination_location.id
            elif previous_state == 'ready_for_deployment':
                if record.origin_location:
                    record.lot_id.location_id = record.origin_location.id

    def write(self, vals):
        lot_updated = 'lot_id' in vals or 'lot_serial_number' in vals

        previous_containers = {}

        for record in self:
            if 'state' in vals:
                new_state = vals['state']
                previous_state = record.state
                record._handle_location_transfer(record, new_state, previous_state)

            if lot_updated and record.lot_id and record.lot_id.container:
                previous_containers[record.id] = record.lot_id.container

        result = super().write(vals)

        return result
