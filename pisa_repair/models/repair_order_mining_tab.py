from odoo import models, fields, api, _
from datetime import datetime

class RepairOrderFields(models.Model):
    _inherit = 'repair.order'

    is_invisible = fields.Boolean(
        string="Is Invisible",
        compute="_compute_is_invisible",
        store=False
    )

    initial_state = fields.Many2many(
        'repair.initial.state',
        'repair_order_initial_state_rel',
        'repair_order_id',
        'initial_state_id',
        string="Initial State",
        ondelete='restrict'
    )

    replaced_components = fields.Many2many(
        'repair.replaced.components',
        'repair_order_replaced_components_rel',
        'repair_order_id',
        'replaced_component_id',
        string="Replaced Components",
        ondelete='restrict'
    )
    
    final_resolution = fields.Many2many(
        'repair.final.resolution',
        'repair_order_final_resolution_rel',
        'repair_order_id',
        'final_resolution_id',
        string="Final Resolution",
        ondelete='restrict'
    )

    evidence_image = fields.Binary(
        string='Failure Evidence',
        help="Upload an image as evidence of the failure."
    )

    extraction = fields.Boolean(
        string='Will Extraction Be Necessary',
        default=False
    )

    needs_rest = fields.Boolean(
        string='Is it necessary to let it rest',
        default=False
    )

    resting = fields.Boolean(
        string="Resting",
        default=False
    )

    start_rest = fields.Datetime(
        string="Start Rest",
        readonly=True
    )

    end_rest = fields.Datetime(
        string="End Rest",
        readonly=True
    )

    all_steps_completed = fields.Boolean(
        string="All Steps Completed",
        compute="_compute_all_steps_completed",
        store=False
    )

    lot_id = fields.Many2one('stock.lot', string="Lot/Serial Number")

    lot_repair_type = fields.Char(
        string="Repair Type",
        compute='_compute_lot_repair_type',
        store=False
    )

    performed_steps_rel_ids = fields.One2many(
        'repair.order.steps.rel',
        'order_id',
        string='Performed Steps'
    )

    def action_start_rest(self):
        for record in self:
            if record.needs_rest:
                record.resting = True
                record.start_rest = fields.Datetime.now()
                record._manage_tags(
                    tag_to_add_xmlid='pisa_repair.resting_mode',
                    tag_to_remove_xmlid='pisa_repair.confirmed'
                )
                record.message_post(
                    body=f"⏳ Rest started: {record.start_rest.strftime('%Y-%m-%d %H:%M:%S')}",
                    subtype_xmlid="mail.mt_note"
                )

    def action_end_rest(self):
        for record in self:
            if record.resting:
                record.resting = False
                record.end_rest = fields.Datetime.now()
                time_diff = record.end_rest - record.start_rest
                total_seconds = int(time_diff.total_seconds())

                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60

                formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"

                record._manage_tags(
                    tag_to_add_xmlid='pisa_repair.confirmed',
                    tag_to_remove_xmlid='pisa_repair.resting_mode'
                )

                record.message_post(
                    body=f"""⏳ Rest ended: {record.end_rest.strftime('%Y-%m-%d %H:%M:%S')}
⏱ Total rest time: {formatted_time}""",
                    subtype_xmlid="mail.mt_note"
                )
    
    @api.depends('state')
    def _compute_is_invisible(self):
        for record in self:
            record.is_invisible = not record.id or record.state == 'draft'

    @api.depends('performed_steps_rel_ids.completed')
    def _compute_all_steps_completed(self):
        for record in self:
            if record.performed_steps_rel_ids:
                all_completed = all(record.performed_steps_rel_ids.mapped('completed'))
                record.all_steps_completed = all_completed
                
                if not all_completed:
                    record.needs_rest = False
            else:
                record.all_steps_completed = False
                record.needs_rest = False
 
    @api.depends('product_id.miner_cooling_type')
    def _compute_lot_repair_type(self):
        for record in self:
            if not record.product_id: 
                record.lot_repair_type = 'general'
                continue
            
            cooling_type = record.product_id.miner_cooling_type
            record.lot_repair_type = self._get_repair_type_from_container(cooling_type) or 'general'

    @api.model
    def create(self, vals):
        record = super(RepairOrderFields, self).create(vals)

        repair_type = record.lot_repair_type or 'general'

        steps = self.env['repair.steps'].search([
            '|', ('type', '=', repair_type), ('type', '=', 'general')
        ])

        steps_rel = [(0, 0, {'step_id': step.id, 'completed': False}) for step in steps]

        record.performed_steps_rel_ids = steps_rel

        return record
    
    def _get_repair_type_from_container(self, cooling_type):
        if not cooling_type:
            return 'general'
        if cooling_type == 'immersion':
            return 'immersion'
        elif cooling_type == 'hydro':
            return 'hydro'
        elif cooling_type == 'fan':
            return 'fan'
        return 'general'
