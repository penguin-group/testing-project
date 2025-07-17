from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_purchase_order(self, company_id, origins, values):
        # Extend this method to set the assignee to the current user
        res = super()._prepare_purchase_order(company_id, origins, values)
        res['assignee_id'] = self.env.user.id
        return res