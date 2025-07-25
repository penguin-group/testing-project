from odoo import api, models, fields

class BancoInterfisa(models.Model):
    _name = 'payroll.bank.interfisa'
    _description = 'Banco Interfisa'

    name = fields.Char(string="Nombre")