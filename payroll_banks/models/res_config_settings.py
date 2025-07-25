from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    payroll_bank_definition_id = fields.Many2one("payroll.bank.definition")
    salary_payment_bank = fields.Many2one(related="payroll_bank_definition_id.salary_payment_bank", string="Bank used for employees salary:", store=True, readonly=False)

