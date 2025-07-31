from odoo import models


class EmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    def _search_filter_for_expense(self, operator, value):
        res = super()._search_filter_for_expense(operator, value)
        user = self.env.user
        employee = user.employee_id

        if user.has_groups("hr_expense_flow.group_hr_expense_user_advanced"):
            # Allow seeing all employees in the same company
            res = [
                "|",
                ("company_id", "=", False),
                ("company_id", "=", employee.company_id.id),
            ]

        return res
