# -*- coding: utf-8 -*-
# from odoo import http


# class RubricaPersonalizado(http.Controller):
#     @http.route('/rubrica_personalizado/rubrica_personalizado', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rubrica_personalizado/rubrica_personalizado/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('rubrica_personalizado.listing', {
#             'root': '/rubrica_personalizado/rubrica_personalizado',
#             'objects': http.request.env['rubrica_personalizado.rubrica_personalizado'].search([]),
#         })

#     @http.route('/rubrica_personalizado/rubrica_personalizado/objects/<model("rubrica_personalizado.rubrica_personalizado"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rubrica_personalizado.object', {
#             'object': obj
#         })
