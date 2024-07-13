from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    no_contact_main_vat_duplicates = fields.Boolean(
        string='Control estricto de duplicidad de RUC',
        default=False,
        readonly=False
    )
