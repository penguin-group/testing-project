from odoo import fields, models, api, _

class InvoiceEditCurrencyRate(models.TransientModel):
    _name = 'invoice.edit.currency.rate'
    _description = 'Edit Currency Rate'

    currency_rate = fields.Float(string='Currency Rate', digits=(12, 6))

    def _get_invoice(self):
        return self.env['account.move'].browse(self._context.get('active_id', False))
    
    def default_get(self, fields_list):
        res = super(InvoiceEditCurrencyRate, self).default_get(fields_list)
        res['currency_rate'] = self._get_invoice().invoice_currency_rate
        return res

    def apply_currency_rate(self):
        self.ensure_one()
        inv = self._get_invoice()
        inv.invoice_currency_rate = self.currency_rate
        inv.line_ids._compute_totals()
        return {'type': 'ir.actions.act_window_close'}
