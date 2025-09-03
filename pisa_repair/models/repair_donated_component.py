from odoo import models, fields

class RepairDonatedComponent(models.Model):
    _name = "repair.donated.component"
    _description = "Donated components from irreparable miners"

    name = fields.Char("Component Name", required=True)
    serial_number = fields.Char("Serial Number")
    description = fields.Text("Description")
    available = fields.Boolean("Available", default=True)

    ticket_origin_id = fields.Many2one(
        "repair.order", string="Origin Ticket", ondelete="cascade"
    )
    ticket_dest_id = fields.Many2one(
        "repair.order", string="Destination Ticket"
    )