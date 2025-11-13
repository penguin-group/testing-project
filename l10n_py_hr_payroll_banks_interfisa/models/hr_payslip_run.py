from odoo import fields, models


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def action_payment_report(self, export_format='xlsx'):
        salary_payment_bank = self.env['ir.config_parameter'].sudo().get_param("res_config_settings.salary_payment_bank")
        if salary_payment_bank == 'interfisa':
            super().action_payment_report(export_format)
        else:  # if interfisa is not set as our bank, we just let odoo create its usual CSV file
            super().action_payment_report(export_format='csv')
