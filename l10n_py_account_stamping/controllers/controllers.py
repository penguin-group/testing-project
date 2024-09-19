# -*- coding: utf-8 -*-
# from odoo import http


# class L10nPyAccountStamping(http.Controller):
#     @http.route('/l10n_py_account_stamping/l10n_py_account_stamping', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_py_account_stamping/l10n_py_account_stamping/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_py_account_stamping.listing', {
#             'root': '/l10n_py_account_stamping/l10n_py_account_stamping',
#             'objects': http.request.env['l10n_py_account_stamping.l10n_py_account_stamping'].search([]),
#         })

#     @http.route('/l10n_py_account_stamping/l10n_py_account_stamping/objects/<model("l10n_py_account_stamping.l10n_py_account_stamping"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_py_account_stamping.object', {
#             'object': obj
#         })

