from odoo import models, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.model
    def create(self, vals):
        # Check if being created as supplier
        if vals.get('supplier_rank', 0) > 0:
            if not vals.get('country_id'):
                raise ValidationError(_("Suppliers must have a country set."))
        return super().create(vals)

    def write(self, vals):
        for partner in self:
            # Check if becoming a supplier
            supplier_rank = vals.get('supplier_rank', partner.supplier_rank)
            if supplier_rank > 0:
                # Partner is becoming a supplier
                if not (vals.get('country_id') or partner.country_id):
                    raise ValidationError(_("Suppliers must have a country set."))
        return super().write(vals)