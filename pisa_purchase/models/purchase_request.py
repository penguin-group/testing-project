from odoo import models, fields, api


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    project_id = fields.Many2one('project.project', string='Project')
    request_assistance = fields.Boolean(string='Request Assistance')
    