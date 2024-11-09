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
        return self.env.company.country_code == 'PY'
