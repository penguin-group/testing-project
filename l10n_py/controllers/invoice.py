from odoo import http
import hashlib

class InvoiceController(http.Controller):
    @http.route('/invoice/check', auth='public', website=True)
    def index(self, invoice_id, token):
        if token == self.generate_token(str(invoice_id)):
            invoice = http.request.env['account.move'].sudo().search([('id', '=', int(invoice_id))])
            if invoice:
                return http.request.render('l10n_py.online_invoice', {'invoice': invoice})
            else:
                return http.request.render('l10n_py.invoice_not_found')
        else:
            return http.request.render('l10n_py.invalid_token')

    def generate_token(self, invoice_id):
        secret_phrase = invoice_id + "amakakeruriunohirameki"
        return hashlib.sha256(secret_phrase.encode('utf-8')).hexdigest()
