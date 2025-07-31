from odoo import models, _
from odoo.exceptions import UserError


class AccountChangeLockDate(models.TransientModel):
    _inherit = 'account.change.lock.date'

    def change_lock_date(self):
        """
        Override this method to also grant permission to the CFO group
        """
        self.ensure_one()
        if self.env.user.has_group('account.group_account_manager') or self.env.user.has_group('pisa_account.group_account_cfo'): 
            exception_vals_list = self._prepare_exception_values()
            changed_lock_date_values = self._prepare_lock_date_values(exception_vals_list=exception_vals_list)

            if exception_vals_list:
                self.env['account.lock_exception'].create(exception_vals_list)

            self._change_lock_date(changed_lock_date_values)
        else:
            raise UserError(_('Only Billing Administrators are allowed to change lock dates!'))
        return {'type': 'ir.actions.act_window_close'}
    
