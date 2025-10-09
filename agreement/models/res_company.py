from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    notify_ten_days_prior = fields.Boolean("Notify 10 days prior", default=False)
    notify_one_day_prior = fields.Boolean("Notify 1 day prior", default=False)
    notify_on_the_date = fields.Boolean("Notify on the date", default=False)
