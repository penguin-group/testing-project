from odoo import api, models, fields

class PayrollBankInherit(models.Model):
    _inherit = 'payroll.bank.definition'

    @api.model
    def _get_available_banks(self):
        res = super(PayrollBankInherit, self)._get_available_banks()
        res.append('payroll.bank.interfisa')
        return res
