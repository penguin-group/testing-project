# -*- coding: utf-8 -*-
# from odoo import http


# class ConsolidationAutomation(http.Controller):
#     @http.route('/consolidation_automation/consolidation_automation', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/consolidation_automation/consolidation_automation/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('consolidation_automation.listing', {
#             'root': '/consolidation_automation/consolidation_automation',
#             'objects': http.request.env['consolidation_automation.consolidation_automation'].search([]),
#         })

#     @http.route('/consolidation_automation/consolidation_automation/objects/<model("consolidation_automation.consolidation_automation"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('consolidation_automation.object', {
#             'object': obj
#         })

