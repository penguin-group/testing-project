# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    expense_reimbursement_account_id = fields.Many2one(
        comodel_name="account.account",
        related="company_id.expense_reimbursement_account_id",
        domain="[('account_type', '=', 'liability_payable'), ('reconcile', '=', True)]",
        readonly=False,
        check_company=True,
    )

    clearing_journal_id = fields.Many2one(
        "account.journal",
        related="company_id.clearing_journal_id",
        readonly=False,
        check_company=True,
        domain="[('type', '=', 'general')]",
    )

    emp_reimbursement_transient_account_id = fields.Many2one(
        "account.account",
        related="company_id.emp_reimbursement_transient_account_id",
        readonly=False,
        check_company=True
    )
