from odoo import models, fields, api

class CostCenter(models.Model):
    _name = 'cost.center'

    cost_center_id = fields.Many2one('account.analytic.account', string='Cost Center')
    percentage = fields.Float(string='Percentage', required=True)