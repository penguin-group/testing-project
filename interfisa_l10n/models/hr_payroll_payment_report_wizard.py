from odoo import api, models, fields


class HrPayrollPaymentReportWizard(models.TransientModel):
    _inherit = 'hr.payroll.payment.report.wizard'

    export_format = fields.Selection(selection_add=[('xlsx', 'Excel')], ondelete={'xlsx': 'set default'})

    def generate_payment_report(self):
        super().generate_payment_report()

        salary_payment_bank = self.env['ir.config_parameter'].get_param("res_config_settings.salary_payment_bank")

        if self.export_format == 'xlsx' and salary_payment_bank == 'interfisa':
            print("hello interfisa")
