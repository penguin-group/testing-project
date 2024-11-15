from odoo import models, api, exceptions, _

class ReportInvoice(models.AbstractModel):
    _name = 'report.l10n_py.invoice_report_template'
    _description = 'Self-Printable Invoice Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        invoices = self.env['account.move'].browse(docids)

        for invoice in invoices:
            if invoice.move_type not in ['out_invoice', 'out_refund']:
                raise exceptions.UserError(_("You cannot print this invoice because it is not a customer invoice."))

        # If validation passes, generate the report values
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': invoices,
        }
