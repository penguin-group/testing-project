from odoo import api, fields, models, tools, _


class CurrencyRate(models.Model):
    _inherit = 'res.currency.rate'


    rate_type = fields.Selection([
        ('buying', 'Buying'),
        ('selling', 'Selling')
    ], string='Rate Type', default='selling')
    