# -*- coding: utf-8 -*-
# from odoo import http


# class IfrsReports(http.Controller):
#     @http.route('/ifrs_reports/ifrs_reports', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ifrs_reports/ifrs_reports/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ifrs_reports.listing', {
#             'root': '/ifrs_reports/ifrs_reports',
#             'objects': http.request.env['ifrs_reports.ifrs_reports'].search([]),
#         })

#     @http.route('/ifrs_reports/ifrs_reports/objects/<model("ifrs_reports.ifrs_reports"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ifrs_reports.object', {
#             'object': obj
#         })
