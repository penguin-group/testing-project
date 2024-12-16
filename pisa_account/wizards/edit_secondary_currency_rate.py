from odoo import fields, models, api, _

class EditSecondaryCurrencyRate(models.TransientModel):
    _name = 'edit.secondary.currency.rate'
    _description = 'Edit Secondary Currency Rate'

    secondary_currency_rate = fields.Float(
        string='Secondary Currency Rate', 
        digits=(12, 12)
    )
    inverse_secondary_currency_rate = fields.Float(
        string='Inverse Secondary Currency Rate', 
        digits=(12,12),
    )

    @api.onchange('secondary_currency_rate')
    def _onchange_secondary_currency_rate(self):
        for record in self:
            record.inverse_secondary_currency_rate = 1 / self.secondary_currency_rate

    @api.onchange('inverse_secondary_currency_rate')
    def _onchange_inverse_secondary_currency_rate(self):
        for record in self:
            record.secondary_currency_rate = 1 / self.inverse_secondary_currency_rate

    def _get_invoice(self):
        return self.env['account.move'].browse(self._context.get('active_id', False))
    
    def default_get(self, fields_list):
        res = super(EditSecondaryCurrencyRate, self).default_get(fields_list)
        res['secondary_currency_rate'] = self._get_invoice().invoice_secondary_currency_rate
        return res

    def apply_secondary_currency_rate(self):
        self.ensure_one()
        inv = self._get_invoice()
        inv.invoice_secondary_currency_rate = self.secondary_currency_rate
        inv.line_ids._compute_secondary_balance()
        return {'type': 'ir.actions.act_window_close'}
