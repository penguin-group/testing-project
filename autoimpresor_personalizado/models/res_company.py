from locale import currency
from odoo import models, api, fields, exceptions,_




class ResCompany(models.Model):
    _inherit = 'res.company'

    datos_banco = fields.Html(string='Datos de cuentas bancarias')

