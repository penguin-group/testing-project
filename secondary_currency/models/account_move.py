from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    company_secondary_currency_id = fields.Many2one(
        string='Company Secondary Currency',
        related='company_id.secondary_currency_id', readonly=True,
    )
