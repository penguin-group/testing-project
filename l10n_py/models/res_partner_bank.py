from odoo import models, fields, api


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    document_type = fields.Selection([
        ("ci", "CI"),
        ("crt", "CRT"),
        ("pasap", "PASAP"),
        ("ruc", "RUC"),
        ("crp", "CRP"),
        ("tdef", "TDEF"),
        ("cod_swit", "COD. SWIT")
    ], string="Document Type", default="ci")
    bank_country_code = fields.Char(related='bank_id.country.code', readonly=True)
    partner_document_number = fields.Char("Account Holder Doc. Number",
                                          compute="_compute_partner_document_number",
                                          readonly=False,
                                          store=True)

    @api.depends("document_type", "partner_id")
    def _compute_partner_document_number(self):
        for rec in self:
            if not rec.partner_id:
                rec.partner_document_number = ""
                continue

            if rec.document_type == 'ruc':
                rec.partner_document_number = rec.partner_id.vat or ""
            elif rec.document_type == 'ci':
                if rec.partner_id.employee_ids:
                    rec.partner_document_number = rec.partner_id.employee_ids[0].identification_id or ""
                else:
                    rec.partner_document_number = ""
            else:
                rec.partner_document_number = ""