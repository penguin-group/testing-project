from odoo import models, fields, _

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def get_exempt_5_10(self):
        self.ensure_one()
        pyg = self.env.ref('base.PYG')
        
        def convert_amount(amount):
            amount = round(amount, 2)
            if self.currency_id == pyg:
                return amount
            elif self.currency_id != pyg and self.company_id.currency_id == pyg:
                return amount / self.move_id.invoice_currency_rate
            else:
                return self.currency_id._convert(amount, pyg, self.company_id, self.date)
        
        base10 = 0
        vat10 = 0
        base5 = 0
        vat5 = 0
        exempt = 0
        taxable_imports = 0
        
        price_total = self.price_total
        
        if self.tax_ids and self.tax_ids[0].amount == 10:
            base10 += convert_amount(price_total / 1.1)
            vat10 += convert_amount(price_total / 11)
        if self.tax_ids and self.tax_ids[0].amount == 5:
            base5 += convert_amount(price_total / 1.05)
            vat5 += convert_amount(price_total / 21)
        if (self.tax_ids and self.tax_ids[0].amount == 0) or not self.tax_ids:
            exempt += convert_amount(price_total)

        # Handle import clearance invoices
        if self.move_id.move_type == "out_invoice" and self.move_id.import_clearance:
            if self.account_id.vat_import:
                vat10 = exempt
                base10 = vat10 * 10
                taxable_imports = base10
            exempt = 0

        return base10, vat10, base5, vat5, exempt, taxable_imports
