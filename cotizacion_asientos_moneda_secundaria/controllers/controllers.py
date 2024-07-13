# -*- coding: utf-8 -*-
# from odoo import http


# class CotizacionImportacion(http.Controller):
#     @http.route('/cotizacion_importacion/cotizacion_importacion', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cotizacion_importacion/cotizacion_importacion/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cotizacion_importacion.listing', {
#             'root': '/cotizacion_importacion/cotizacion_importacion',
#             'objects': http.request.env['cotizacion_importacion.cotizacion_importacion'].search([]),
#         })

#     @http.route('/cotizacion_importacion/cotizacion_importacion/objects/<model("cotizacion_importacion.cotizacion_importacion"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cotizacion_importacion.object', {
#             'object': obj
#         })
