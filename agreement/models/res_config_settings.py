from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    notify_ten_days_prior = fields.Boolean("Notify 10 days prior", config_parameter='res_config_settings.notify_ten_days_prior', default=False)
    notify_one_day_prior = fields.Boolean("Notify 1 day prior", config_parameter='res_config_settings.notify_one_day_prior', default=False)
    notify_on_the_date = fields.Boolean("Notify on the date", config_parameter='res_config_settings.notify_on_the_date', default=False)
