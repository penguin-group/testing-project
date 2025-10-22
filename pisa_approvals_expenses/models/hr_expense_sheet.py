from odoo import fields, models, api, _
from odoo.exceptions import UserError


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    approval_id = fields.Many2one("approval.request",
                                  readonly=False,
                                  string="Approval Request")
    approval_amount = fields.Float(related="approval_id.amount", string="Approval Amount")

    employee_user_id = fields.Many2one(
        'res.users',
        related='employee_id.user_id',
        string="Employee's User",
        store=False,
    )

    outstanding_balance = fields.Monetary(string='Outstanding Balance',
                                          compute='_compute_outstanding_balance',
                                          currency_field='currency_id',
                                          readonly=True,
                                          store=True)

    @api.onchange("approval_id")
    def _check_approval_and_expense_currency(self):
        if self.approval_id.currency_id != self.currency_id:
            raise UserError(_("The approval request's currency (%s) doesn't match the expense report's currency (%s).", self.approval_id.currency_id.name, self.currency_id.name))


    @api.depends('approval_id', 'currency_id', 'total_amount', 'total_amount_currency')
    def _compute_outstanding_balance(self):
        for report in self:
            if not report.approval_id:
                report.outstanding_balance = 0
                continue

            report.outstanding_balance = report.approval_id.related_vendor_bill.amount_total - report.total_amount_currency
