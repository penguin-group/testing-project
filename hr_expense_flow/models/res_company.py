# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    expense_reimbursement_account_id = fields.Many2one(
        "account.account",
        string="Reimbursement Account",
        check_company=True,
        domain="[('account_type', '=', 'liability_payable'), ('reconcile', '=', True)]", 
        help="The account used to record the reimbursement to employee of expenses.",
    )

    clearing_journal_id = fields.Many2one(
        "account.journal",
        string="Clearing Journal",
        check_company=True,
        domain="[('type', '=', 'general')]",
        help="The company's default journal used when creating the clearing entry.",
    )

    emp_reimbursement_transient_account_id = fields.Many2one(
        "account.account", string="Transient account for employee reimbursement",
        check_company=True
    )
