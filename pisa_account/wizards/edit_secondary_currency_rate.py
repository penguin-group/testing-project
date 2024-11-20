from odoo import fields, models, api, _

class EditSecondaryCurrencyRate(models.TransientModel):
    _name = 'edit.secondary.currency.rate'
    _description = 'Edit Secondary Currency Rate'

    secondary_currency_rate = fields.Float(string='Secondary Currency Rate', digits=(12, 6))

    def _get_invoice(self):
        return self.env['account.move'].browse(self._context.get('active_id', False))
    
    def default_get(self, fields_list):
        res = super(EditSecondaryCurrencyRate, self).default_get(fields_list)
        res['secondary_currency_rate'] = self._get_invoice().secondary_currency_rate
        return res

    def apply_currency_rate(self):
        self.ensure_one()
        inv = self._get_invoice()
        inv.invoice_currency_rate = self.currency_rate
        return {'type': 'ir.actions.act_window_close'}
