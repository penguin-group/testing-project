from odoo import models
from . import account_report

class BalanceSheetCustomHandler(account_report.AccountReportPisaCustomHandler):
    _name = 'account.balance.sheet.report.handler'
    _inherit = 'account.report.custom.handler'
    _description = "Balance Sheet Custom Handler"

