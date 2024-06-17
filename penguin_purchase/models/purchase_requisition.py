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

    process_followed = fields.Boolean(string="Process was followed", required=False, compute='_compute_process_followed', store=True )
    number_of_signatories = fields.Char(string="Number of Signatories", compute='_compute_number_of_signatories',
                                        store=True)

    @api.model
    def create(self, vals):
        res = super(PurchaseRequisition, self).create(vals)
        if 'line_ids' in vals:
            for line in vals['line_ids']:
                line[2].update({
                    'product_classification': 'materials',  # Default classification
                })
        return res

    @api.depends('signature1', 'signature2', 'signature3')
    def _compute_process_followed(self):
        for record in self:
            record.process_followed = bool(record.signature1 or record.signature2 or record.signature3)

    @api.depends('signature1', 'signature2', 'signature3')
    def _compute_number_of_signatories(self):
        for record in self:
            signatories = sum(1 for sig in [record.signature1, record.signature2, record.signature3] if sig)
            record.number_of_signatories = str(signatories)


class PurchaseRequisitionLine(models.Model):
    _inherit = 'purchase.requisition.line'

    product_classification = fields.Selection(
        [('labor', 'Labor'), ('materials', 'Materials'), ('units', 'Units')],
        string='Product Classification',
        required=True,
    )
    document_ids = fields.Many2many('ir.attachment', string='Documents')



