from odoo import models, fields, api


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    project_id = fields.Many2one('project.project', string='Project')
    request_assistance = fields.Boolean(string='Request Assistance')
    off_budget = fields.Boolean(string='Off-Budget', tracking=True)

    def _link_attachments_to_purchase_order(self, purchase_order):
        """
        Create new attachment records for the purchase order that reference 
        the same stored files from the purchase request attachments.
        """
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'purchase.request'),
            ('res_id', '=', self.id)
        ])
        
        for attachment in attachments:
            # Create new attachment record but reference the same store_fname
            self.env['ir.attachment'].create({
                'name': attachment.name,
                'type': attachment.type,
                'res_model': 'purchase.order',
                'res_id': purchase_order.id,
                'store_fname': attachment.store_fname,  # Reference same file
                'mimetype': attachment.mimetype,
                'datas': attachment.datas,  # This references the same file content
            })
