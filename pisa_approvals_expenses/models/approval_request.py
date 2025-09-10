from odoo import models, _, fields, Command
from odoo.exceptions import UserError


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    has_bank_account = fields.Selection(related="category_id.has_bank_account")
    has_currency = fields.Selection(related="category_id.has_currency")
    currency_id = fields.Many2one("res.currency", string="Currency")
    req_owner_related_partner_id = fields.Many2one(
        'res.partner',
        related='request_owner_id.partner_id',
        store=True
    )
    bank_account_id = fields.Many2one(
        "res.partner.bank",
        domain="[('partner_id', '=', req_owner_related_partner_id)]",
        string="Bank Account"
    )
    related_vendor_bill = fields.Many2one("account.move", string="Vendor Bills")

    def action_confirm(self):
        super(ApprovalRequest, self).action_confirm()

        if self.currency_id.name != self.bank_account_id.currency_id.name:
            raise UserError(_("The approval request's currency (%s) doesn't match the bank account's currency (%s).",
                              self.currency_id.name, self.bank_account_id.currency_id.name))


    def _create_employee_advancement_invoice(self, amount):
        """Create a vendor bill for employee advancement and set transient and payable accounts on it."""
        self.ensure_one()

        partner = self.req_owner_related_partner_id
        journal = self.env.company.clearing_journal_id
        company = self.company_id or self.env.company
        transient_acc = company.emp_reimbursement_transient_account_id

        if not transient_acc:
            raise UserError("Missing transient account configuration for employee reimbursement.")

        move_vals = {
            'move_type': 'in_invoice',
            'journal_id': journal.id,
            'partner_id': partner.id,
            'invoice_date': self.date or self.date_confirmed,
            'invoice_origin': self.name or 'Employee Advancement',
            'ref': self.name or 'Employee Advancement',
            'currency_id': self.currency_id.id,
            'partner_bank_id': self.bank_account_id.id,
            'invoice_line_ids': [
                Command.create({
                    'name': "Employee Advancement",
                    'account_id': transient_acc.id,
                    'price_unit': amount,
                    'tax_ids': False,
                }),
            ]
        }

        move = self.env['account.move'].sudo().create(move_vals)

        payable_line = move.line_ids.filtered(lambda l: l.credit > 0)
        if payable_line:
            payable_line.account_id = company.expense_reimbursement_account_id.id

        move._post()
        return move

    def action_approve(self, approver=None):
        super(ApprovalRequest, self).action_approve()

        if self.category_id.approval_type == 'create_vendor_bill_adv':
            move = self._create_employee_reimbursement_invoice(self.amount)
            move.approval_id = self.id
            self.related_vendor_bill = move.id


    def action_view_vendor_bill(self):
        self.ensure_one()
        account_move = self.env['account.move'].search([('id', '=', self.related_vendor_bill.id)])
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "domain": [('id', 'in', account_move.ids)],
            "context": {"create": False, 'default_move_type': 'in_invoice'},
            "name": _("Vendor Bills"),
            'view_mode': 'list,form',
        }









