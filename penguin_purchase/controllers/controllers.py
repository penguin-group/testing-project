# -*- coding: utf-8 -*-
# from odoo import http


# class PenguinPurchase(http.Controller):
#     @http.route('/penguin_purchase/penguin_purchase', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/penguin_purchase/penguin_purchase/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('penguin_purchase.listing', {
#             'root': '/penguin_purchase/penguin_purchase',
#             'objects': http.request.env['penguin_purchase.penguin_purchase'].search([]),
#         })

#     @http.route('/penguin_purchase/penguin_purchase/objects/<model("penguin_purchase.penguin_purchase"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('penguin_purchase.object', {
#             'object': obj
#         })
