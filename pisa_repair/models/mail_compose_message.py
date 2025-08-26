from odoo import models, api

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def action_send_mail(self):
        res = super(MailComposeMessage, self).action_send_mail()

        if self.env.context.get('default_model') == 'sale.order' and self.env.context.get('default_res_ids'):
            sale_orders = self.env['sale.order'].browse(self.env.context['default_res_ids'])
            for sale_order in sale_orders:

                for line in sale_order.order_line:
                    for quotation in line.related_quotation_ids:
                        if quotation.state == 'draft':
                            quotation.write({'state': 'sent'})

        return res