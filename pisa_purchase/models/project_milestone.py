from odoo import models, fields, api

class ProjectMilestone(models.Model):
    _name = 'project.milestone'
    _inherit = ['project.milestone', 'mail.thread', 'mail.activity.mixin']

    purchase_line_id = fields.Many2one('purchase.order.line', string='Purchase Order Line', tracking=True, related='task_ids.purchase_line_id', store=True)
    purchase_qty = fields.Float(string="Purchase Quantity")

    @api.onchange('is_reached')
    def _onchange_is_reached(self):
        if self.is_reached:
            self._update_purchase_order_line_quantities()

    def _update_purchase_order_line_quantities(self):
        for milestone in self:
            for line in milestone.task_ids.purchase_line_id:
                line.qty_received += milestone.purchase_qty

