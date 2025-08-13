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
        """Return list of available banks to add to salary_payment_bank selection.

        E.g: ('interfisa', 'Interfisa')
        """
        banks = self.env['payroll.bank.definition']._get_available_banks()
        return banks
