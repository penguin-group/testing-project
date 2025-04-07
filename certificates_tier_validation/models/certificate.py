from odoo import models


class Certificate(models.Model):
    _name = "certificate"
    _inherit = ["certificate", "tier.validation"]

    _tier_validation_manual_config = False
