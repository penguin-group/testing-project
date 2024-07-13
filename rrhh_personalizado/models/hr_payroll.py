from odoo import api, fields, models


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    def custom_action_print_payslip(self):
        return self.env.ref('rrhh_personalizado.recibo_custom').report_action(self)
