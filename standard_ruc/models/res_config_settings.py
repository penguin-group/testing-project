from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    no_contact_main_vat_duplicates = fields.Boolean(
        string='Control estricto de duplicidad de RUC',
        related='company_id.no_contact_main_vat_duplicates',
        help='No se aceptarán contactos sin empresa matriz con un RUC ya existente en el sistema',
        readonly=False
    )
