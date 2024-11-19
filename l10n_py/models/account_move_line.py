from odoo import models, fields, _

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    amount_exempt = fields.Monetary(
        string='Exempt amount',
        compute='_compute_fields_for_py_reports',
    )
    amount_base10 = fields.Monetary(
        string='Base VAT 10% amount',
        compute='_compute_fields_for_py_reports',
    )
    amount_vat10 = fields.Monetary(
        string='VAT 10% amount',
        compute='_compute_fields_for_py_reports',
    )
    amount_base5 = fields.Monetary(
        string='Base VAT 5% amount',
        compute='_compute_fields_for_py_reports',
    )
    amount_vat5 = fields.Monetary(
        string='VAT 5% amount',
        compute='_compute_fields_for_py_reports',
    )
    amount_taxable_imports = fields.Monetary(
        string='Taxable imports amount',
        compute='_compute_fields_for_py_reports',
    )

    def _compute_fields_for_py_reports(self):
        for record in self:
            record.amount_base10 = record.amount_vat10 = record.amount_base5 = record.amount_vat5 = record.amount_exempt = record.amount_taxable_imports = 0
            
            if any([tax.amount == 0 for tax in record.tax_ids]):
                record.amount_exempt = abs(record.balance)
            elif record.tax_line_id and record.tax_line_id.amount == 10:
                record.amount_base10 = record.tax_base_amount
                record.amount_vat10 = abs(record.balance)
            elif record.tax_line_id and record.tax_line_id.amount == 5:
                record.amount_base5 = record.tax_base_amount
                record.amount_vat5 = abs(record.balance)

            # Handle import clearance invoices
            if record.move_id.move_type == "out_invoice" and record.move_id.import_clearance:
                if record.account_id.vat_import:
                    record.amount_vat10 = exempt
                    record.amount_base10 = record.amount_vat10 * 10
                    record.amount_taxable_imports = record.amount_base10
                exempt = 0
            
