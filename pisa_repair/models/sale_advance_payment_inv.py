from odoo import models, _
from odoo.exceptions import UserError

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

        if any(so.is_only_micro for so in sale_orders):
            raise UserError(_("You do not have sufficient permissions"))

        return super().create_invoices()