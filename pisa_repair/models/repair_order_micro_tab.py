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

    is_in_testing = fields.Boolean(
        string="Is in Testing",
        compute="_compute_is_in_testing",
        store=False
    )

    is_testing_passed = fields.Boolean(
        string="Testing Passed",
        compute="_compute_is_testing_passed",
        store=False
    )

    @api.depends('tag_ids', 'tag_ids.name')
    def _compute_is_testing_passed(self):
        for rec in self:
            names = {(n or '').strip().lower() for n in rec.tag_ids.mapped('name')}
            rec.is_testing_passed = (
                'testing passed' in names or 'testing_passed' in names
                or 'ready for deployment' in names or 'ready_for_deployment' in names
            )

    @api.depends('tag_ids', 'tag_ids.name', 'state')
    def _compute_is_in_testing(self):
        for record in self:
            tag_names = {(name or '').strip().lower() for name in record.tag_ids.mapped('name')}
            record.is_in_testing = 'testing' in tag_names

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

    def _get_tag_model(self):
        field = self._fields.get('tag_ids')
        if not field or not getattr(field, 'comodel_name', None):
            raise ValidationError(_("Tagging is not configured on repair.order (missing tag_ids/comodel)."))
        return self.env[field.comodel_name]

    def _get_or_create_repair_tag(self, name):
        Tag = self._get_tag_model()
        tag = Tag.search([('name', '=ilike', name)], limit=1)
        if not tag:
            tag = Tag.create({'name': name})
        return tag

    def _search_tag_any(self, names):
        """Busca la primera tag que coincida (case-insensitive) entre varias opciones."""
        Tag = self._get_tag_model()
        for n in names:
            t = Tag.search([('name', '=ilike', n)], limit=1)
            if t:
                return t
        return Tag.browse()

    def _ensure_under_repair(self):
        for rec in self:
            if rec.state != 'under_repair':
                raise ValidationError(_("This action is only available in 'Under Repair' state."))
            
    def action_start_testing(self):
        for rec in self:
            if not rec.is_in_repair:
                raise ValidationError(_("You can start testing only when 'under_repair' tag is set."))
            testing_tag = rec._get_or_create_repair_tag('testing')
            under_repair_tag = rec._get_or_create_repair_tag('under_repair')
            diag_tag = rec._search_tag_any(['under diagnosis', 'under_diagnosis'])

            cmds = [(4, testing_tag.id), (4, under_repair_tag.id)]
            if diag_tag:
                cmds.append((3, diag_tag.id))
            rec.write({'tag_ids': cmds})
            rec.message_post(body=_("Testing started."))

    def action_back_to_under_repair(self):
        for rec in self:
            testing_tag = rec._search_tag_any(['testing'])
            under_repair_tag = rec._get_or_create_repair_tag('under_repair')
            passed_tag = rec._search_tag_any(['testing passed', 'testing_passed'])
            ready_tag = rec._search_tag_any(['ready for deployment', 'ready_for_deployment'])

            cmds = [(4, under_repair_tag.id)]
            for t in (testing_tag, passed_tag, ready_tag):
                if t:
                    cmds.append((3, t.id))
            rec.write({'tag_ids': cmds})
            rec.message_post(body=_("Testing failed: back to Under Repair."))

    def action_finish_testing(self):
        for rec in self:
            testing_tag = rec._search_tag_any(['testing'])
            passed_tag = rec._get_or_create_repair_tag('testing_passed')

            cmds = []
            if testing_tag:
                cmds.append((3, testing_tag.id))
            cmds += [(4, passed_tag.id)]
            rec.write({'tag_ids': cmds})
            rec.message_post(body=_("Testing finished and approved."))

    def action_back_to_under_diagnosis(self):
        for rec in self:
            testing_tag = rec._search_tag_any(['testing'])
            diag_tag = rec._get_or_create_repair_tag('under_diagnosis')
            under_repair_tag = rec._search_tag_any(['under repair', 'under_repair'])
            passed_tag = rec._search_tag_any(['testing passed', 'testing_passed'])
            ready_tag = rec._search_tag_any(['ready for deployment', 'ready_for_deployment'])

            cmds = [(4, diag_tag.id)]
            for t in (testing_tag, under_repair_tag, passed_tag, ready_tag):
                if t:
                    cmds.append((3, t.id))
            rec.write({'tag_ids': cmds})
            rec.message_post(body=_("Testing failed: back to Under Diagnosis."))

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


    parent_is_validated = fields.Boolean(related='repair_id.is_validated', store=False)
    parent_is_in_diagnostic = fields.Boolean(related='repair_id.is_in_diagnostic', store=False)
    parent_is_in_repair = fields.Boolean(related='repair_id.is_in_repair', store=False)

    @api.depends('item', 'repair_type', 'sn')
    def _compute_name(self):
        for r in self:
            parts = [r.item or '', r.repair_type or '', r.sn or '']
            r.name = ' | '.join([p for p in parts if p])

