from odoo import http
import hashlib
import os

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


class Res90(http.Controller):
    @http.route('/res90/download_file/', auth='public')
    def index(self, **kw):
        if kw.get('file'):
            filepath = os.path.join('/tmp/', kw.get('file'))
            filename = kw.get('filename', kw.get('file') + '.txt')
            
            # Open the file in binary mode
            with open(filepath, 'rb') as file_content:
                file_data = file_content.read()
                
                # Create a Response object with the file content
                response = http.request.make_response(
                    file_data,
                    headers=[
                        ('Content-Disposition', f'attachment; filename="{filename}"'),
                        ('Content-Type', 'application/octet-stream'),
                    ]
                )
                return response