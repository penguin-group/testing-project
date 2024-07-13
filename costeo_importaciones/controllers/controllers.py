# -*- coding: utf-8 -*-
# from odoo import http


# class CosteoImportaciones(http.Controller):
#     @http.route('/costeo_importaciones/costeo_importaciones', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/costeo_importaciones/costeo_importaciones/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('costeo_importaciones.listing', {
#             'root': '/costeo_importaciones/costeo_importaciones',
#             'objects': http.request.env['costeo_importaciones.costeo_importaciones'].search([]),
#         })

#     @http.route('/costeo_importaciones/costeo_importaciones/objects/<model("costeo_importaciones.costeo_importaciones"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('costeo_importaciones.object', {
#             'object': obj
#         })
