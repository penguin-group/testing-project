from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    salary_payment_bank = fields.Selection(
        selection=lambda self: self._get_available_banks(),
        string="Bank used for employees salary",
        config_parameter='res_config_settings.salary_payment_bank'
    )

    @api.model
    def _get_available_banks(self):
        """Return list of (model_name, label).
        E.g: (payroll.bank.itau, Itau)
        """
        banks = self.env['payroll.bank.definition']._get_available_banks()
        return [(bank_model, bank_model.replace('payroll.bank.', '').capitalize()) for bank_model in banks]
