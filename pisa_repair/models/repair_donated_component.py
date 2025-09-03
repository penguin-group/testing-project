from odoo import models, fields, api

class RepairDonatedComponent(models.Model):
    _name = "repair.donated.component"
    _description = "Donated components from irreparable miners"

    name = fields.Selection([
        ('psu', 'PSU'),
        ('cb', 'CB'),
        ('hash', 'Hash'),
        ('data_cable', 'Data Cable'),
        ('cooling_plate_psu', 'Cooling Plate PSU'),
        ('cooling_plate_hash', 'Cooling Plate Hash'),
    ], string="Component", required=True)
    serial_number = fields.Char("Serial Number")
    description = fields.Text("Description")
    available = fields.Boolean(
        string="Available",
        compute="_compute_is_available",
        store=True
    )

    ticket_origin_id = fields.Many2one(
        "repair.order", string="Origin Ticket", ondelete="cascade"
    )
    ticket_dest_id = fields.Many2one(
        "repair.order", string="Destination Ticket"
    )

    @api.depends("ticket_dest_id")
    def _compute_is_available(self):
        """Si hay ticket destino, está disponible = True, si no, False."""
        for rec in self:
            rec.available = True if rec.ticket_dest_id else False

    @api.onchange("ticket_dest_id")
    def _onchange_ticket_dest_id(self):
        """Refrescar en la vista cuando se selecciona/quita un ticket destino."""
        for rec in self:
            rec.available = True if rec.ticket_dest_id else False