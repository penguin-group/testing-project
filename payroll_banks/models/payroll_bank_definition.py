from odoo import api, fields, models

class PayrollBankDefinition(models.AbstractModel):
    _name = 'payroll.bank.definition'
    _description = 'Abstract base for bank integration'

    @api.model
    def _get_available_banks(self):
        return []


