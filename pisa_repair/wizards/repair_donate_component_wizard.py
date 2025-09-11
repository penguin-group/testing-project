from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo import _

class RepairDonateComponentWizard(models.TransientModel):
    _name = "repair.donate.component.wizard"
    _description = "Wizard for registering donated components"

    component_ids = fields.One2many(
        "repair.donate.component.line",
        "wizard_id",
        string="Components to donate",
    )

    def action_confirm(self):
        active_id = self.env.context.get("active_id")
        if active_id:
            ticket = self.env["repair.order"].browse(active_id)
            for line in self.component_ids:
                self.env["repair.donated.component"].create({
                    "name": line.name,
                    "serial_number": line.serial_number,
                    "description": line.description,
                    "ticket_origin_id": ticket.id,
                })

            tag_under_diagnosis = self.env.ref("pisa_repair.under_diagnosis", raise_if_not_found=False)
            tag_donor = self.env.ref("pisa_repair.donor", raise_if_not_found=False)

            updates = []
            if tag_under_diagnosis and tag_under_diagnosis.id in ticket.tag_ids.ids:
                updates.append((3, tag_under_diagnosis.id)) 
            if tag_donor:
                updates.append((4, tag_donor.id))

            if updates:
                ticket.write({'tag_ids': updates})

            ticket.state = "done"

        return {"type": "ir.actions.act_window_close"}


class RepairDonateComponentLine(models.TransientModel):
    _name = "repair.donate.component.line"
    _description = "Donated component wizard lines"

    wizard_id = fields.Many2one("repair.donate.component.wizard")
    name = fields.Selection([
        ('psu', 'PSU'),
        ('cb', 'CB'),
        ('hash', 'Hash'),
        ('data_cable', 'Data Cable'),
        ('cooling_plate_psu', 'Cooling Plate PSU'),
        ('cooling_plate_hash', 'Cooling Plate Hash'),
    ], string="Component", required=True)
    serial_number = fields.Char("Serial number")
    description = fields.Text("Description")

    @api.constrains("name", "wizard_id")
    def _check_unique_component_per_wizard(self):
        for rec in self:
            if rec.name and rec.wizard_id:
                duplicates = rec.wizard_id.component_ids.filtered(lambda l: l.name == rec.name)
                if len(duplicates) > 1:
                    raise ValidationError(_("The component '%s' is already selected in this wizard.") % rec.name)