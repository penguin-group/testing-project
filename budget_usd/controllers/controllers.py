# -*- coding: utf-8 -*-
# from odoo import http


# class BudgetUsd(http.Controller):
#     @http.route('/budget_usd/budget_usd', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/budget_usd/budget_usd/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('budget_usd.listing', {
#             'root': '/budget_usd/budget_usd',
#             'objects': http.request.env['budget_usd.budget_usd'].search([]),
#         })

#     @http.route('/budget_usd/budget_usd/objects/<model("budget_usd.budget_usd"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('budget_usd.object', {
#             'object': obj
#         })
