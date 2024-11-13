# -*- coding: utf-8 -*-

from odoo import models, fields, api, release


class ResCompany(models.Model):
    _inherit = 'res.company'

    inventory_book_base_report_bs = fields.Many2one(
        'account.report',
        string='Base Report for Balance Sheet',
    )
    inventory_book_base_report_is = fields.Many2one(
        'account.report',
        string='Base Report for Income Statement',
    )
    show_inventory_book_base_report_bs_details = fields.Boolean(
        string='Show Account Details',
        default=True
    )

    def in_paraguay(self):
        py_menu_ext_ids = [
            'l10n_py.book_registration_report_menu',
            'l10n_py.book_registration_menu',
            'l10n_py.invoice_authorization_menu',
            'l10n_py.report_res90_menu',
            'l10n_py.report_vat_purchase_wizard_menu',
            'l10n_py.report_vat_sale_wizard_menu',
        ]
        py_menu_ids = self.env['ir.ui.menu'].browse([self.env.ref(py_menu_ext_id).id for py_menu_ext_id in py_menu_ext_ids])
        in_paraguay = self.env.company.country_code == 'PY'
        if in_paraguay:
            py_menu_ids.sudo().write({
                'show': True,
            })
        else:
            py_menu_ids.sudo().write({
               'show': False,
            })
        return in_paraguay
