from odoo import api, fields, models

class PayrollBankDefinition(models.Model):
    _name = 'payroll.bank.definition'

    @api.model
    def _get_available_banks(self):
        return []

    salary_payment_bank = fields.Many2one(
        comodel_name="ir.model",
        domain=lambda self: [("model", "in", self._get_available_banks())],
    )


