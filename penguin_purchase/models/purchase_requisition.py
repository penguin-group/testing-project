from odoo import models, fields, api

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    analytic_account_ids = fields.Many2many('account.analytic.account', string='Analytic Accounts')
