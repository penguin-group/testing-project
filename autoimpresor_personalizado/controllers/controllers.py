# -*- coding: utf-8 -*-
# from odoo import http


# class PenguinModulo(http.Controller):
#     @http.route('/penguin_modulo/penguin_modulo', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/penguin_modulo/penguin_modulo/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('penguin_modulo.listing', {
#             'root': '/penguin_modulo/penguin_modulo',
#             'objects': http.request.env['penguin_modulo.penguin_modulo'].search([]),
#         })

#     @http.route('/penguin_modulo/penguin_modulo/objects/<model("penguin_modulo.penguin_modulo"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('penguin_modulo.object', {
#             'object': obj
#         })
