from odoo import api, fields, models


class InvoiceAuthorization(models.Model):
    _inherit = 'invoice.authorization'

    proveedores_timbrado_id = fields.Integer(
        string='Proveedores Timbrado Id',
        copy=False,
        readonly=True,
        help='Id of the timbrado in the old database'
    )

    def validate_authorization_format(self, name):
        # Deactivate this validation while the module secondary_currency_migration is installed
        return False
