from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    assignee_id = fields.Many2one('res.users', string='Assignee', help='User responsible for this RFQ')
    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('rfq_completed', 'RFQ Completed'),
        ('technical_review', 'Technical Review'),
        ('sourcing_strategy', 'Sourcing Strategy'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    milestone_count = fields.Integer(compute='_compute_milestone_count', export_string_translation=False)

    def _compute_milestone_count(self):
        read_group = self.env['project.milestone']._read_group(
            [('purchase_line_id', 'in', self.order_line.ids)],
            ['purchase_line_id'],
            ['__count'],
        )
        line_data = {purchase_line.id: count for purchase_line, count in read_group}
        for order in self:
            order.milestone_count = sum(line_data.get(line.id, 0) for line in order.order_line)


    def action_view_milestone(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Milestones'),
            'domain': [('purchase_line_id', 'in', self.order_line.ids)],
            'res_model': 'project.milestone',
            'views': [(self.env.ref('pisa_purchase.project_milestone_view_list_inherit').id, 'list')],
            'view_mode': 'list',
        }