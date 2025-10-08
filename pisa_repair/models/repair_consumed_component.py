from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class RepairConsumedComponent(models.Model):
    _name = "repair.consumed.component"
    _description = "Components consumed by a repair order"

    repair_order_id = fields.Many2one(
        "repair.order", string="Repair Order", ondelete="cascade"
    )
    donated_component_id = fields.Many2one(
        "repair.donated.component",
        string="Component",
        required=True,
        domain="[('used', '=', False)]",
    )
    ticket_origin_id = fields.Many2one(
        related="donated_component_id.ticket_origin_id",
        string="Origin Ticket",
        store=True,
        readonly=True
    )

    serial_number = fields.Char(
        related="donated_component_id.serial_number",
        string="Serial Number", store=False, readonly=True
    )
    
    description = fields.Text(
        related="donated_component_id.description",
        string="Description", store=False, readonly=True
    )

    is_validated = fields.Boolean(related="repair_order_id.is_validated", store=False)
    is_in_repair = fields.Boolean(related="repair_order_id.is_in_repair", store=False)
    is_micro = fields.Boolean(related="repair_order_id.is_micro", store=False)

    @api.onchange("donated_component_id")
    def _onchange_donated_component_id(self):
        for rec in self:
            if rec.donated_component_id:
                rec.donated_component_id.used = True
                rec.donated_component_id.ticket_dest_id = rec.repair_order_id
                rec.donated_component_id.ticket_origin_id._update_donor_scrapped_tags()
            else:
                rec.donated_component_id.used = False
                rec.donated_component_id.ticket_dest_id = False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.donated_component_id:
                rec.donated_component_id.used = True
                rec.donated_component_id.ticket_dest_id = rec.repair_order_id
                rec.donated_component_id.ticket_origin_id._update_donor_scrapped_tags()
        return records
    
    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.donated_component_id:
                rec.donated_component_id.used = True
                rec.donated_component_id.ticket_dest_id = rec.repair_order_id
                rec.donated_component_id.ticket_origin_id._update_donor_scrapped_tags()
        return res

    def unlink(self):
        for rec in self:
            if rec.donated_component_id:
                rec.donated_component_id.used = False
                rec.donated_component_id.ticket_dest_id = False
                rec.donated_component_id.ticket_origin_id._update_donor_scrapped_tags()
        return super().unlink()
    
    def action_remove_component(self):
        for rec in self:
            if rec.donated_component_id:
                rec.donated_component_id.used = False
                rec.donated_component_id.ticket_dest_id = False
            if rec.id:
                rec.unlink()
            else:
                _logger.warning("Tried to remove a component without a valid record ID.")