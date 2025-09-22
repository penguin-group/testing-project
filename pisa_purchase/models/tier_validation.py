from odoo import models, fields


class TierValidation(models.AbstractModel):
    _inherit = 'tier.validation'

    def _validate_tier(self, tiers=False):
        super(TierValidation, self)._validate_tier()

        if all(r.status == 'approved' for r in self.review_ids):
            self.state = 'purchase'
