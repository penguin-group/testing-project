from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    assignee_id = fields.Many2one('res.users', string='Assignee', help='User responsible for this RFQ')

    def _compute_next_review(self):
        # Override original method to change the next review string
        for rec in self:
            review = rec.review_ids.sorted("sequence").filtered(
                lambda x: x.status == "pending"
            )[:1]
            rec.next_review = review.name if review else ""
