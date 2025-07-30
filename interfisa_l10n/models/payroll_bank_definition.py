from odoo import api, models, fields

class PayrollBankDefinitionInherit(models.AbstractModel):
    _inherit = 'payroll.bank.definition'

    @api.model
    def _get_available_banks(self):
        res = super(PayrollBankDefinitionInherit, self)._get_available_banks()
        res.append(('interfisa', 'Interfisa'))  # append tuple; this goes to the salary_payment_bank field in res.config.settings
        return res
