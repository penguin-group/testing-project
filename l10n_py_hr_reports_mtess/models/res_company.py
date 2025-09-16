from odoo import models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    def get_menu_ext_ids(self):
        original_ids = super(ResCompany, self).get_menu_ext_ids()
        return original_ids + [
            'l10n_py_hr_reports_mtess.menu_hr_reports_mtess'
        ]
