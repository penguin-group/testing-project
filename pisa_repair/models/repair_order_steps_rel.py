from odoo import models, fields, api
from odoo.exceptions import ValidationError


class RepairOrderStepsRel(models.Model):
    _name = 'repair.order.steps.rel'
    _description = 'Repair Order Steps Relation'
    _order = 'step_sequence, id'

    order_id = fields.Many2one(
        'repair.order', 
        string="Orden de Reparación", 
        required=True, 
        ondelete='cascade'
    )

    step_id = fields.Many2one(
        'repair.steps', 
        string='Step', 
        required=True, 
        ondelete='restrict'
    )

    step_name = fields.Char(
        string="Step Name",
        related="step_id.name",
        store=False,
        readonly=True
    )

    step_type = fields.Selection(
        string="Type",
        related="step_id.type",
        store=False,
        readonly=True
    )

    step_url = fields.Char(
        string="URL",
        related="step_id.url",
        store=False,
        readonly=True
    )

    is_noc = fields.Boolean(
        string="Is NOC",
        compute="_compute_is_noc",
        store=False
    )

    @api.depends('order_id.is_noc')
    def _compute_is_noc(self):
        for record in self:
            record.is_noc = bool(record.order_id.is_noc)

    
    is_validated = fields.Boolean(
        string="Is Validated",
        related="order_id.is_validated",
        store=False,
        readonly=True
    )

    step_sequence = fields.Integer(
        string="Sequence",
        related="step_id.sequence",
        store=False,
        readonly=True
    )

    completed = fields.Boolean(string='Completed', default=False)

    _sql_constraints = [
        ('unique_order_step', 'unique(order_id, step_id)', 'This step is already added to this order.')
    ]

    def _check_step_type(self, order, step):
        if step.type not in ['general', order.lot_repair_type]:
            raise ValidationError(f"You cannot add a step of type {step.type}. Only steps of type 'general' or '{order.lot_repair_type}' are allowed.")

    def write(self, vals):
        for record in self:
            new_step = self.env['repair.steps'].browse(vals.get('step_id', record.step_id.id))
            self._check_step_type(record.order_id, new_step)
        return super(RepairOrderStepsRel, self).write(vals)
    
    @api.model
    def create(self, vals):
        order = self.env['repair.order'].browse(vals.get('order_id'))
        step = self.env['repair.steps'].browse(vals.get('step_id'))
        self._check_step_type(order, step)
        return super(RepairOrderStepsRel, self).create(vals)
