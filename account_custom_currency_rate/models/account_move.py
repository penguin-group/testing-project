from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.constrains('journal_id', 'partner_id')
    def _check_vendor_country(self):
        for move in self:
            if move.move_type == 'in_invoice' and move.journal_id.local_suppliers:
                if not move.partner_id.country_id:
                    raise UserError(_("If the Vendor Bill is under a 'Proveedores Nacionales' journal, the vendor country must be set."))

    def edit_currency_rate(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'invoice.edit.currency.rate',
            'view_mode': 'form',
            'view_id': self.env.ref('account_custom_currency_rate.invoice_edit_currency_rate_view_form').id,
            'target': 'new',
            'context': {'active_id': self.id}
        }