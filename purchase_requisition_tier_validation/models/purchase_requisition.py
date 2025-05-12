from odoo import models


class PurchaseRequisition(models.Model):
    _name = "purchase.requisition"
    _inherit = ["purchase.requisition", "tier.validation"]

    _tier_validation_manual_config = False
