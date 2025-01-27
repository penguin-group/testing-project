from odoo import models
from odoo.addons.account_reports.models.account_report import AccountReportCustomHandler

class AccountReportPisaCustomHandler(AccountReportCustomHandler):
    _name = 'account.report.custom.handler'
    _description = 'Account Report PISA Custom Handler'

    def _get_custom_display_config(self):
        return {
            'css_custom_class': 'pisa_report_pdf',
        }