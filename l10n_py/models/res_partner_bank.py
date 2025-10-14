from odoo import models, fields, api


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    bank_country_code = fields.Char(related='bank_id.country.code', readonly=True)
    partner_document_number = fields.Char("Account Holder Doc. Number",
                                          compute="_compute_partner_document_number",
                                          readonly=False)

    def _compute_partner_document_number(self):
        for rec in self:
            if not rec.partner_id:
                rec.partner_document_number = ""
                continue

            rec.partner_document_number = rec.partner_id.vat or ""