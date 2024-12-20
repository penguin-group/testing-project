# -*- coding: utf-8 -*-
import base64
from odoo import http
from odoo.http import request


class BookRegistrationController(http.Controller):
    @http.route('/binary/download', type='http', auth='user')
    def download_binary_file(self, **kwargs):
        record_id = kwargs.get('record_id')
        if record_id:
            record = request.env['book.registration.report'].browse(int(record_id))
            binary_data = record.report_file
            file_data = base64.b64decode(binary_data)
            headers = [
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', http.content_disposition(record.report_file_name))
            ]
            return request.make_response(file_data, headers)
