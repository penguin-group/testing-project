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
            if any([
                self.env.context.get('from_contacts'),
                self.env.context.get('from_purchase'),
                self.env.context.get('res_partner_search_mode') == 'supplier'
            ]):
                # If becoming a supplier or already a supplier, check if country is set
                supplier_rank = vals.get('supplier_rank', partner.supplier_rank)
                if supplier_rank > 0:
                    if not (vals.get('country_id') or partner.country_id):
                        raise ValidationError(_("Suppliers must have a country set."))
        return super().write(vals)