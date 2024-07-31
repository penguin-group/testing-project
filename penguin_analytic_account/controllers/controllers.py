# -*- coding: utf-8 -*-
# from odoo import http


# class PenguinAnalyticAccount(http.Controller):
#     @http.route('/penguin_analytic_account/penguin_analytic_account', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/penguin_analytic_account/penguin_analytic_account/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('penguin_analytic_account.listing', {
#             'root': '/penguin_analytic_account/penguin_analytic_account',
#             'objects': http.request.env['penguin_analytic_account.penguin_analytic_account'].search([]),
#         })

#     @http.route('/penguin_analytic_account/penguin_analytic_account/objects/<model("penguin_analytic_account.penguin_analytic_account"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('penguin_analytic_account.object', {
#             'object': obj
#         })

