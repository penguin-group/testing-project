from odoo import fields, models, api, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    sync_with_department_analytic_acc = fields.Boolean(
        string=_("Use Analytic Account from Department"),
        default=True,
        help=_("When checked, the analytic account will automatically sync with the department's analytic account")
    )

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        'Analytic Account',
        check_company=True,
        readonly=False
    )

    @api.depends('department_id.department_analytic_account_id', 'sync_with_department_analytic_acc')
    def _compute_analytic_account_id(self):
        """Compute analytic account based on department and flag"""
        for contract in self:
            # if sync_with_department_analytic_acc is checked and the contract has a department,
            # then this contract's analytic account shall be the same as the department's.
            if contract.sync_with_department_analytic_acc and contract.department_id:
                contract.analytic_account_id = contract.department_id.department_analytic_account_id

    @api.onchange('sync_with_department_analytic_acc')
    def _onchange_sync_with_department_analytic_acc(self):
        """When sync_with_department_analytic_acc is checked, sync with department"""

        # if the user checks sync_with_department_analytic_acc and the contract already has
        # a department, I grab the analytic account from the department. If the contract does
        # not have a department, nothing happens. However, this would rarely be the case as
        # the department is pulled immediately when selecting an employee.
        if self.sync_with_department_analytic_acc and self.department_id:
            self.analytic_account_id = self.department_id.department_analytic_account_id

    @api.onchange('department_id')
    def _onchange_department_id(self):
        """When department changes, update analytic account if in sync with department"""
        if self.sync_with_department_analytic_acc and self.department_id:
            self.analytic_account_id = self.department_id.department_analytic_account_id

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):
        """When analytic account is manually changed, uncheck sync_with_department_analytic_acc"""

        # Even if the user does not interact with the boolean flag, if they modify
        # the contract's analytic account the boolean will be unchecked.
        if self.sync_with_department_analytic_acc and self.department_id and self.analytic_account_id != self.department_id.department_analytic_account_id:
            self.sync_with_department_analytic_acc = False

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to set initial analytic account from department"""
        contracts = super().create(vals_list)

        for contract in contracts:
            if contract.sync_with_department_analytic_acc and contract.department_id:
                contract.write({
                    'analytic_account_id': contract.department_id.department_analytic_account_id.id
                })

        return contracts
