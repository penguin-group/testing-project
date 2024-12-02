# -*- coding: utf-8 -*-
# from odoo import http


# class PisaAccountMigration(http.Controller):
#     @http.route('/pisa_account_migration/pisa_account_migration', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pisa_account_migration/pisa_account_migration/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pisa_account_migration.listing', {
#             'root': '/pisa_account_migration/pisa_account_migration',
#             'objects': http.request.env['pisa_account_migration.pisa_account_migration'].search([]),
#         })

#     @http.route('/pisa_account_migration/pisa_account_migration/objects/<model("pisa_account_migration.pisa_account_migration"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pisa_account_migration.object', {
#             'object': obj
#         })

