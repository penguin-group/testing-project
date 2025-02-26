from odoo import models, fields, api, _

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    project_task_ids = fields.One2many('project.task', 'purchase_line_id', string='Tasks')
    milestones_ids = fields.One2many('project.milestone', 'purchase_line_id', string=' Milestones')
    
