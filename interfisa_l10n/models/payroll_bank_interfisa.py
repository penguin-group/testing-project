from odoo import api, models, fields


class PayrollBankInterfisa(models.AbstractModel):
    _name = 'payroll.bank.interfisa'
    _inherit = 'payroll.bank.definition'

    name = fields.Char('Name', required=True)

    def process_payroll_xlsx(self, employee):
        pass