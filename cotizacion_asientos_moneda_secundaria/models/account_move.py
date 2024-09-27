from odoo import _, api, fields, models,exceptions
from odoo.tools.float_utils import float_compare, float_is_zero



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    
    def compute_secondary_values(self):
        secondary_currency_id = self.env.company.secondary_currency_id
        if not secondary_currency_id:
            return
        if secondary_currency_id == self.currency_id:
            tipo_cambio = 0
            if self.balance and self.amount_currency:
                tipo_cambio = abs(self.balance) / abs(self.amount_currency)
        else:
            if self.move_id.freeze_currency_rate:
                tipo_cambio=self.move_id.currency_rate
            else:
                tipo_cambio = secondary_currency_id.rate_ids.filtered(lambda x: x.name <= self.date)
                if tipo_cambio[0].rate < 1:
                    tipo_cambio[0].rate = 1 / tipo_cambio[0].rate
                tipo_cambio = round(tipo_cambio[0].rate,2)
            if not tipo_cambio:
                raise exceptions.ValidationError('No existe un tipo de cambio definido para la fecha %s'%self.date)
        if tipo_cambio>0:
            debit_ms = round(self.debit / tipo_cambio)
            credit_ms = round(self.credit / tipo_cambio)
            balance_ms = round(self.balance / tipo_cambio)
        else:
            debit_ms = 0
            credit_ms = 0
            balance_ms = 0
        self.write({'debit_ms': debit_ms,
                    'credit_ms': credit_ms,
                    'secondary_currency_id': secondary_currency_id.id,
                    'tipo_cambio': tipo_cambio,
                    'balance_ms': balance_ms})
    
    

    def _apply_price_difference(self):
        svl_vals_list = []
        aml_vals_list = []
        for line in self:
            line = line.with_company(line.company_id)
            po_line = line.purchase_line_id
            uom = line.product_uom_id or line.product_id.uom_id

            # Don't create value for more quantity than received
            quantity = po_line.qty_received - (po_line.qty_invoiced - line.quantity)
            quantity = max(min(line.quantity, quantity), 0)
            if float_is_zero(quantity, precision_rounding=uom.rounding):
                continue

            layers = line._get_valued_in_moves().stock_valuation_layer_ids.filtered(lambda svl: svl.product_id == line.product_id and not svl.stock_valuation_layer_id)
            if not layers:
                continue
            
            if not self.move_id.freeze_currency_rate:
                new_svl_vals_list, new_aml_vals_list = line._generate_price_difference_vals(layers)
            else:
                new_svl_vals_list=[] 
                new_aml_vals_list=[]
            svl_vals_list += new_svl_vals_list
            aml_vals_list += new_aml_vals_list
        return self.env['stock.valuation.layer'].sudo().create(svl_vals_list), self.env['account.move.line'].sudo().create(aml_vals_list)