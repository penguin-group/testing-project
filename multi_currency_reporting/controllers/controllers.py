# -*- coding: utf-8 -*-
# from odoo import http


# class MultiCurrencyReporting(http.Controller):
#     @http.route('/multi_currency_reporting/multi_currency_reporting', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/multi_currency_reporting/multi_currency_reporting/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('multi_currency_reporting.listing', {
#             'root': '/multi_currency_reporting/multi_currency_reporting',
#             'objects': http.request.env['multi_currency_reporting.multi_currency_reporting'].search([]),
#         })

#     @http.route('/multi_currency_reporting/multi_currency_reporting/objects/<model("multi_currency_reporting.multi_currency_reporting"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('multi_currency_reporting.object', {
#             'object': obj
#         })

