from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Site(models.Model):
    _name = 'pisa.site'
    _description = 'Site'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, id desc'

    name = fields.Char(
        string="Description", 
        required=True, 
        tracking=True
    )
    tag_ids = fields.Many2many(
        'pisa.site.tag',
        string="Tags", 
        tracking=True
    )
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Stage', default='new', tracking=True)
    state_id = fields.Many2one(
        'pisa.site.state', 
        string="State",
        default=lambda self: self._get_default_state(),
        tracking=True
    )
    country_id = fields.Many2one(
        'res.country', 
        string="Country", 
        tracking=True
    )
    capacity = fields.Float(
        string="Capacity (MW)", 
        default=0.0, 
        tracking=True
    )
    probability = fields.Integer(
        string="Probability (%)", 
        default=0, 
        required=True, 
        tracking=True
    )
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Very High')
    ], default='1', string='Priority')
    voltage_level = fields.Float(
        string="Voltage Level (V)", 
        required=True, 
        tracking=True
    )
    project_brief = fields.Html(
        string="Project Brief", 
        tracking=True
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        required=True,
        default=lambda self: self.env.ref('base.main_company')
    )

    @api.constrains('probability')
    def _check_probability(self):
        for record in self:
            if not 0 <= record.probability <= 100:
                raise ValidationError(_("Probability must be between 0 and 100."))

    @api.model
    def _get_default_state(self):
        return self.env['pisa.site.state'].search([('name', '=', 'New')], limit=1).id 