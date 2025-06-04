from odoo import models, fields


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    petty_cash_account_ids = fields.Many2many(
        comodel_name='account.account',
        string='Petty Cash Accounts',
        help='Select accounts for petty cash.'
    )