from odoo import models, fields, api 


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    cost_center_ids = fields.Many2many('cost.center', string='Cost Center')

    selection_notes = fields.Char(string="Comments", required=False, )

    signature1 = fields.Binary(string="Signature 1", required=False, ) #firma Head Engineering
    signature2 = fields.Binary(string="Signature 2", required=False, ) #firma Project Manager
    signature3 = fields.Binary(string="Signature 3", required=False, ) #firma Head of Procurement
    signature4 = fields.Binary(string="Signature 4", required=False, ) #firma adicional de aprob
    signature5 = fields.Binary(string="Signature 5", required=False, ) #firma adicional de aprob
