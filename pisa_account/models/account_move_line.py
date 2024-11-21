from odoo import models, fields, api, tools

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'  

    @api.depends('currency_id', 'company_id', 'move_id.invoice_currency_rate', 'move_id.date')
    def _compute_secondary_currency_rate(self):
        for line in self:
            line.secondary_currency_rate = line.move_id.invoice_secondary_currency_rate

    @api.depends('balance')
    def _compute_secondary_balance(self):
        # Override the original method from the secondary_currency module to modify the rounding, 
        # which should be 0 decimal places, although the rounding field in the currency settings is set to two decimal places.
        for line in self:
            if line.company_secondary_currency_id:
                if line.display_type in ('line_section', 'line_note'):
                    line.secondary_balance = False
                elif line.currency_id == line.company_secondary_currency_id:
                    if line.company_secondary_currency_id.name == "PYG":
                        line.secondary_balance = tools.float_round(line.amount_currency, 0)
                    else:
                        line.secondary_balance = line.company_secondary_currency_id.round(line.amount_currency)
                else:
                    if line.company_secondary_currency_id.name == "PYG":
                        line.secondary_balance = tools.float_round(line.balance / line.secondary_currency_rate, 0)
                    else:
                        line.secondary_balance = line.company_secondary_currency_id.round(line.balance / line.secondary_currency_rate)
            else:
                line.secondary_balance = 0

    def _compute_fields_for_py_reports(self):
        if self.env.company.sec_currency_id and self.env.company.sec_currency_id.name == 'PYG' and self.env.company.country_code == 'PY':
            for record in self:
                record.amount_base10 = record.amount_vat10 = record.amount_base5 = record.amount_vat5 = record.amount_exempt = record.amount_taxable_imports = 0
                
                if any([tax.amount == 0 for tax in record.tax_ids]):
                    record.amount_exempt = abs(record.secondary_balance)
                elif record.tax_line_id and record.tax_line_id.amount == 10:
                    record.amount_base10 = record.tax_base_amount
                    record.amount_vat10 = abs(record.secondary_balance)
                elif record.tax_line_id and record.tax_line_id.amount == 5:
                    record.amount_base5 = record.tax_base_amount
                    record.amount_vat5 = abs(record.secondary_balance)

                # Handle import clearance invoices
                if record.move_id.move_type == "out_invoice" and record.move_id.import_clearance:
                    if record.account_id.vat_import:
                        record.amount_vat10 = exempt
                        record.amount_base10 = record.amount_vat10 * 10
                        record.amount_taxable_imports = record.amount_base10
                    exempt = 0
        else:
            super(AccountMoveLine, self)._compute_fields_for_py_reports()