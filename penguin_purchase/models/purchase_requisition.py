from odoo import models, fields, api

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    analytic_account_ids = fields.Many2many('account.analytic.account', string='Analytic Accounts')

    cost_center_id = fields.Many2one('analytic_account_ids', string='Cost Center')
    percentage = fields.Float(string='Percentage', required=True)
    selection_notes = fields.Char(string="Comments", required=False, )
