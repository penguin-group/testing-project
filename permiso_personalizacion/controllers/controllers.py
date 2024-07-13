# -*- coding: utf-8 -*-
# from odoo import http


# class PermisoPersonalizacio(http.Controller):
#     @http.route('/permiso_personalizacio/permiso_personalizacio', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/permiso_personalizacio/permiso_personalizacio/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('permiso_personalizacio.listing', {
#             'root': '/permiso_personalizacio/permiso_personalizacio',
#             'objects': http.request.env['permiso_personalizacio.permiso_personalizacio'].search([]),
#         })

#     @http.route('/permiso_personalizacio/permiso_personalizacio/objects/<model("permiso_personalizacio.permiso_personalizacio"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('permiso_personalizacio.object', {
#             'object': obj
#         })
