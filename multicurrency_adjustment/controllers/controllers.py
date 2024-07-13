# -*- coding: utf-8 -*-
# from odoo import http


# class MulticurrencyAdjustment(http.Controller):
#     @http.route('/multicurrency_adjustment/multicurrency_adjustment', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/multicurrency_adjustment/multicurrency_adjustment/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('multicurrency_adjustment.listing', {
#             'root': '/multicurrency_adjustment/multicurrency_adjustment',
#             'objects': http.request.env['multicurrency_adjustment.multicurrency_adjustment'].search([]),
#         })

#     @http.route('/multicurrency_adjustment/multicurrency_adjustment/objects/<model("multicurrency_adjustment.multicurrency_adjustment"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('multicurrency_adjustment.object', {
#             'object': obj
#         })
