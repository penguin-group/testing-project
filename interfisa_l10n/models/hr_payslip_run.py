from odoo import fields, models


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def action_payment_report(self, export_format='xlsx'):
        super().action_payment_report(export_format)
