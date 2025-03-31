from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import clean_context


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    def _do_create_moves(self):
        """
        Override original method to change the behavior of the "paid by the company" option. 
        If the 'create_vendor_bill' field is checked, a vendor bill should be created.
        """

        res = super(HrExpenseSheet, self)._do_create_moves()
        if any(self.expense_line_ids.mapped('create_vendor_bill')) and self.expense_line_ids.filtered(lambda l: l.payment_mode == 'company_account'):
            # Create a vendor bill
            vendor_bills = self.env['account.move']
            for sheet in self:
                vals = sheet._prepare_bills_vals()
                vals.update({
                    'move_type': 'in_invoice',
                    'partner_id': sheet.expense_line_ids[0].vendor_id.id,
                    'invoice_date': sheet.accounting_date,
                    'ref': None,
                })
                vendor_bill = self.env['account.move'].create(vals)
                vendor_bills |= vendor_bill
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
   