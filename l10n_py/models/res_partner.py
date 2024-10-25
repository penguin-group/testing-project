from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import config
from stdnum.py import ruc


class ResPartner(models.Model):
    _inherit = "res.partner"

    vat = fields.Char(copy=False)
    foreign_default_supplier = fields.Boolean(string='Foreign Default Supplier', default=False)

    @api.constrains("vat", "parent_id")
    def _check_vat(self):
        for record in self:
            if record.parent_id or not record.vat:
                continue
            test_condition = config["test_enable"] and not self.env.context.get(
                "test_vat"
            )
            if test_condition:
                continue
            
            record._check_vat_unique()
            if self.env.company.partner_id.country_id.code == 'PY':
                # Validate VAT only if the company is in Paraguay
                record._validate_vat()
    
    def _check_vat_unique(self):
        if self.same_vat_partner_id:
            raise ValidationError(
                _("The VAT %s already exists in another partner.") % self.vat
            )

    def _validate_vat(self):
        is_valid = ruc.is_valid(self.vat)
        if not is_valid:
            raise ValidationError(
                _("The VAT %s is not valid.") % self.vat
            )

    @api.constrains('foreign_default_supplier')
    def _check_foreign_default_supplier(self):
        for record in self:
            if record.foreign_default_supplier and len(self.search([('foreign_default_supplier', '=', True), ('id', '!=', record.id)])):
                raise ValidationError(_("There should only be one default foreign default supplier."))
            
