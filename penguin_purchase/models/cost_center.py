from odoo import models, fields, api

class CostCenter(models.Model):
    _name = 'cost.center'
    _description = 'Cost Center'
    _inherit = 'analytic.mixin'

    #cost_center_id = fields.Many2one('account.analytic.account', string='Cost Center')
    #percentage = fields.Float(string='Percentage', required=True)
    name = fields.Char(string='Cost Center Name', required=True)