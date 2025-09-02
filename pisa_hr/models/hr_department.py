from odoo import models, api, fields


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    department_analytic_account_id = fields.Many2one("account.analytic.account", string="Analytic account for this department")

    def write(self, vals):
        result = super().write(vals)

        if 'department_analytic_account_id' in vals:  # If the department's analytic account has changed
            contracts_to_update = self.env['hr.contract'].search([  # Get relevant contracts
                ('department_id', 'in', self.ids),
                ('sync_with_department_analytic_acc', '=', True)
            ])

            for contract in contracts_to_update:  # Update each contract's analytic account
                contract.analytic_account_id = contract.department_id.department_analytic_account_id

        return result