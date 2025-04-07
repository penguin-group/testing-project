from itertools import groupby
from odoo import models, Command, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import clean_context


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    def _do_create_moves(self):
        """
        Override original method to change the behavior of the "paid by the company" option. 
        If the 'create_vendor_bill' field is checked, a vendor bill should be created for each expense.
        """

        res = super(HrExpenseSheet, self)._do_create_moves()
        if any(self.expense_line_ids.mapped('create_vendor_bill')) and self.expense_line_ids.filtered(lambda l: l.payment_mode == 'company_account'):
            # Create a vendor bill for each expense line that has the 'create_vendor_bill' field checked and is paid by the company
            vendor_bills = self.env['account.move']
            for sheet in self:
                # Filter expense lines that need vendor bills
                expense_lines = sheet.expense_line_ids.sudo().filtered(
                    lambda l: l.create_vendor_bill and l.payment_mode == 'company_account'
                )
                # Create a vendor bill for each expense
                vals_list = []
                for expense in expense_lines:
                    move_line_vals = expense._prepare_move_lines_vals()
                    if move_line_vals:
                        vals_list.append({
                            'name': '/',
                            'invoice_date': sheet.accounting_date,
                            'expense_sheet_id': self.id,
                            'journal_id': self.journal_id.id,
                            'move_type': 'in_invoice',
                            'partner_id': expense.vendor_id.id,
                            'commercial_partner_id': self.employee_id.user_partner_id.id,
                            'currency_id': self.currency_id.id,
                            'line_ids': [Command.create(move_line_vals)],
                            'attachment_ids': [
                                Command.create(attachment.copy_data({'res_model': 'account.move', 'res_id': False, 'raw': attachment.raw})[0])
                                for attachment in expense.message_main_attachment_id]
                        })
                vendor_bills = self.env['account.move'].sudo().create(vals_list)
            res |= vendor_bills
        return res

    def action_open_account_moves(self):
        """
        Replace original method to change the action when the create_vendor_bill field is checked.
        """

        self.ensure_one()
        if self.payment_mode == 'own_account' or (self.payment_mode == 'company_account' and any(self.expense_line_ids.mapped('create_vendor_bill'))):
            res_model = 'account.move'
            record_ids = self.account_move_ids
        else:
            res_model = 'account.payment'
            record_ids = self.account_move_ids.origin_payment_id

        action = {'type': 'ir.actions.act_window', 'res_model': res_model}
        if len(self.account_move_ids) == 1:
            action.update({
                'name': record_ids.name,
                'view_mode': 'form',
                'res_id': record_ids.id,
                'views': [(False, 'form')],
            })
        else:
            action.update({
                'name': _("Journal entries"),
                'view_mode': 'list',
                'domain': [('id', 'in', record_ids.ids)],
                'views': [(False, 'list'), (False, 'form')],
            })
        return action
   