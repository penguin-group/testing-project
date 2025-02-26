from odoo import models, fields, api, _

class ProjectTask(models.Model):
    _inherit = 'project.task'

    purchase_line_id = fields.Many2one(
        'purchase.order.line', 
        string='Purchase Order Line', 
        tracking=True,
        domain="[('order_id.project_id', '=', project_id)]"
    )
    purchase_order_state = fields.Selection(related='purchase_line_id.order_id.state')
    