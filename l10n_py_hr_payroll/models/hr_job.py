from odoo import models, fields, api


class HrJob(models.Model):
    _inherit = 'hr.job'

    is_manager = fields.Boolean(string="Is Manager", help="Check if the job position is for a managerial role.")
