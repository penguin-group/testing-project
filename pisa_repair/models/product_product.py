from odoo import models, fields, api, _

class ProductProduct(models.Model):
    _inherit = 'product.template'

    is_only_micro = fields.Boolean(
        compute='_compute_is_only_micro', 
        store=False
    )

    @api.depends()
    def _compute_is_only_micro(self):
        for order in self:
            order.is_only_micro = self.env.user.has_group('pisa_repair.group_micro') and  not self.env.user.has_group('pisa_repair.group_micro_leader')
    