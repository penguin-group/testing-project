from odoo import models, fields, api, _

class PurchaseRequisitionCreateAlternative(models.TransientModel):
    _inherit = 'purchase.requisition.create.alternative'

    def _get_alternative_values(self):
        values = super(PurchaseRequisitionCreateAlternative, self)._get_alternative_values()
        values.update({
            'assignee_id': self.origin_po_id.assignee_id.id,
            'project_id': self.origin_po_id.project_id.id,
            'use_certificate': self.origin_po_id.use_certificate,
        })
        return values

    @api.model
    def _get_alternative_line_value(self, order_line):
        res = super()._get_alternative_line_value(order_line)
        res.update({
            'analytic_distribution': order_line.analytic_distribution,
        })
        return res

    def action_create_alternative(self):
        # Override this method to copy attachments after PO creation
        res = super(PurchaseRequisitionCreateAlternative, self).action_create_alternative()
        new_po = self.env['purchase.order'].browse(res['res_id'])
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'purchase.order'),
            ('res_id', '=', self.origin_po_id.id)
        ])
        for attachment in attachments:
            self.env['ir.attachment'].create({
                'name': attachment.name,
                'type': attachment.type,
                'res_model': 'purchase.order',
                'res_id': new_po.id,
                'store_fname': attachment.store_fname,
                'mimetype': attachment.mimetype,
                'datas': attachment.datas,
            })
        return res