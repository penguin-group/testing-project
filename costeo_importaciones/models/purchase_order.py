from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    es_importacion=fields.Boolean(string="Es una importacion",default=False)

    def button_reporte_costeo(self):
        view_id=self.env.ref('costeo_importaciones.wizard_costeo_view_form')
        return{
            'type': 'ir.actions.act_window',
            'res_model': 'costeo_importaciones.wizard.costeo',
            'view_mode': 'form',
            'view_id': view_id.id,
            'target': 'new',
            'context':{'default_purchase_id':self.id}
        }