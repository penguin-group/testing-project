from odoo import models, fields

class RepairOrderTagHistory(models.Model):
    _name = 'repair.order.tag.history'
    _description = 'Tag History in Repair Orders'
    _order = 'create_date desc'

    repair_order_id = fields.Many2one('repair.order', string="Repair Order", required=True, ondelete='cascade')
    tag_id = fields.Many2one('repair.tags', string="Tag", required=True)
    user_id = fields.Many2one('res.users', string="Added by", default=lambda self: self.env.user, readonly=True)
    create_date = fields.Datetime(string="Change Date", readonly=True)