from odoo import models, fields, api

class AccountAccount(models.Model):
    _inherit = 'account.account'

    vat_import = fields.Boolean('VAT Import', help="This account is for import VAT")
