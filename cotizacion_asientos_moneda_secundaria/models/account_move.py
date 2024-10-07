from odoo import _, api, fields, models,exceptions
from odoo.tools.float_utils import float_compare, float_is_zero
import operator



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    
    def compute_secondary_values(self):
        company_currency_id = self.env.company.currency_id
        secondary_currency_id = self.env.company.secondary_currency_id

        if not secondary_currency_id:
            return

        if self.move_id.currency_id == secondary_currency_id:
            debit_ms = abs(self.amount_currency) if self.debit else 0
            credit_ms = abs(self.amount_currency) if self.credit else 0
            balance_ms = self.amount_currency
        else: 
            if self.move_id.freeze_currency_rate:
                debit_ms = self.debit * self.move_id.currency_rate
                credit_ms = self.credit * self.move_id.currency_rate
                balance_ms = self.balance * self.move_id.currency_rate
            else:
                debit_ms = company_currency_id._convert(self.debit, secondary_currency_id, self.company_id, self.date)
                credit_ms = company_currency_id._convert(self.credit, secondary_currency_id, self.company_id, self.date)
                balance_ms = company_currency_id._convert(self.balance, secondary_currency_id, self.company_id, self.date)
        
        self.write({
            'debit_ms': debit_ms,
            'credit_ms': credit_ms,
            'balance_ms': balance_ms,
            'secondary_currency_id': secondary_currency_id.id,
            'tipo_cambio': abs(balance_ms) / abs(self.balance),
        })

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