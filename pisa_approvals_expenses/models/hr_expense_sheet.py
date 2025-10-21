from odoo import fields, models, api, _
from odoo.exceptions import UserError


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    approval_id = fields.Many2one("approval.request",
                                  readonly=False,
                                  string="Approval Request")

    employee_user_id = fields.Many2one(
        'res.users',
        related='employee_id.user_id',
        string="Employee's User",
        store=False,
    )

    @api.onchange("approval_id")
    def _check_approval_and_expense_currency(self):
        print(1)
        if self.approval_id.currency_id != self.currency_id:
            raise UserError(_("The approval request's currency (%s) doesn't match the expense report's currency (%s).",
                              self.approval_id.currency_id.name, self.currency_id.name))
