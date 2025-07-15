from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseCurrencyWizard(models.TransientModel):
    _name = 'purchase.currency.wizard'
    _description = 'Set Currency on Purchase Orders'

    currency_id = fields.Many2one('res.currency', string='Currency', required=True)

    def apply_currency(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            raise UserError(_('No purchase orders selected.'))
        orders = self.env['purchase.order'].browse(active_ids)
        for order in orders:
            order.currency_id = self.currency_id
            # Update currency rate based on order's confirmation date if available
            date = order.date_approve or order.date_order or fields.Date.today()
            rate = self.currency_id._get_rates(order.company_id, date)
            if rate:
                order.currency_rate = rate[self.currency_id.id]
        orders._amount_all()
