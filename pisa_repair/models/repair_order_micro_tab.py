from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class RepairOrderFields(models.Model):
    _inherit = 'repair.order'

    diagnostic_note = fields.Text(string="Diagnostic Note")
    repair_note = fields.Text(string="Repair Note")

    has_diagnostic_note = fields.Boolean(
        string="Has Diagnostic Note",
        compute="_compute_has_diagnostic_note",
        store=False
    )

    has_repair_note = fields.Boolean(
        string="Has Repair Note",
        compute="_compute_has_repair_note",
        store=False
    )

    is_in_diagnostic = fields.Boolean(
        string="Is in Diagnostic",
        compute="_compute_is_in_diagnostic",
        store=False
    )

    is_in_repair = fields.Boolean(
        string="Is in Repair",
        compute="_compute_is_in_repair",
        store=False
    )

    @api.depends('diagnostic_note', 'state')
    def _compute_has_diagnostic_note(self):
        for record in self:
            txt = (record.diagnostic_note or "").strip()
            record.has_diagnostic_note = bool(txt)

    @api.depends('repair_note')
    def _compute_has_repair_note(self):
        for record in self:
            txt = (record.repair_note or "").strip()
            record.has_repair_note = bool(txt)

    @api.depends('tag_ids', 'tag_ids.name', 'state')
    def _compute_is_in_diagnostic(self):
        for record in self:
            tag_names = { (name or '').strip().lower() for name in record.tag_ids.mapped('name') }
            record.is_in_diagnostic = ('under diagnosis' in tag_names)

    @api.depends('tag_ids', 'tag_ids.name', 'state')
    def _compute_is_in_repair(self):
        for record in self:
            tag_names = { (name or '').strip().lower() for name in record.tag_ids.mapped('name') }
            record.is_in_repair = ('under repair' in tag_names)
