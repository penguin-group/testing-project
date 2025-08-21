from odoo import models, api, fields


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    department_analytic_account_id = fields.Many2one("account.analytic.account", string="Analytic account for this department")
