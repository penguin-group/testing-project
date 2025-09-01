from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class RepairOrderFields(models.Model):
    _inherit = 'repair.order'

    repair_diag_line_ids = fields.One2many(
        'pisa.repair.diagnosis.line', 'repair_id',
        string="Diagnosis & Repair"
    )

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
            record.is_in_diagnostic = ('under diagnosis' in tag_names) or ('under_diagnosis' in tag_names)

    @api.depends('tag_ids', 'tag_ids.name', 'state')
    def _compute_is_in_repair(self):
        for record in self:
            tag_names = { (name or '').strip().lower() for name in record.tag_ids.mapped('name') }
            record.is_in_repair = ('under repair' in tag_names) or ('under_repair' in tag_names)


class RepairDiagnosisLine(models.Model):
    _name = 'pisa.repair.diagnosis.line'
    _description = 'Diagnosis & Repair'
    _order = 'id desc'

    ITEM_SELECTION = [
        ('ch0', 'ch0'),
        ('ch1', 'ch1'),
        ('ch2', 'ch2'),
        ('psu', 'psu'),
        ('controlboard', 'controlboard'),
        ('cooling_plate', 'cooling plate'),
        ('data_cable', 'data cable'),
        ('water_distributor', 'water distributor'),
        ('fan', 'fan'),
        ('psu_fan', 'psu fan'),
    ]

    REPAIR_TYPE_SELECTION = [
        ('repair', 'Repair'),
        ('replace_new', 'Replace (New)'),
        ('replace_used', 'Replace (Used)'),
    ]

    repair_id = fields.Many2one(
        'repair.order', string='Repair Order', ondelete='cascade', required=True, index=True
    )

    item = fields.Selection(ITEM_SELECTION, string='Item', required=True)
    sn = fields.Char(string='SN / Serial')
    diagnostic = fields.Text(string='Diagnosis Note', required=True)
    repair_note = fields.Text(string='Repair Note')
    repair_type = fields.Selection(REPAIR_TYPE_SELECTION, string='Repair Type', required=True)

    name = fields.Char(string='Description', compute='_compute_name', store=False)


    # === NUEVO: relateds para controlar columnas según el padre ===
    parent_is_validated = fields.Boolean(related='repair_id.is_validated', store=False)
    parent_is_in_diagnostic = fields.Boolean(related='repair_id.is_in_diagnostic', store=False)
    parent_is_in_repair = fields.Boolean(related='repair_id.is_in_repair', store=False)

    @api.depends('item', 'repair_type', 'sn')
    def _compute_name(self):
        for r in self:
            parts = [r.item or '', r.repair_type or '', r.sn or '']
            r.name = ' | '.join([p for p in parts if p])