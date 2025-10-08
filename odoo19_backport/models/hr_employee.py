from odoo import models, _, tools
from odoo.exceptions import RedirectWarning
from odoo.tools import email_normalize

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def action_create_users_confirmation(self):
        raise RedirectWarning(
                message=_("You're about to invite new users. %s users will be created with the default user template's rights. "
                "Adding new users may increase your subscription cost. Do you wish to continue?", len(self.ids)),
                action=self.env.ref('odoo19_backport.action_hr_employee_create_users').id,
                button_text=_('Confirm'),
                additional_context={
                    'selected_ids': self.ids,
                },
            )

    def action_create_users(self):
        def _get_user_creation_notification_action(message, message_type, next_action):
            return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': self.env._("User Creation Notification"),
                        'type': message_type,
                        'message': message,
                        'next': next_action
                    }
                }

        employee_emails = [
            normalized_email
            for employee in self
            for normalized_email in tools.mail.email_normalize_all(employee.work_email)
        ]
        conflicting_users = self.env['res.users']
        if employee_emails:
            conflicting_users = self.env['res.users'].search([
                '|', ('email_normalized', 'in', employee_emails),
                ('login', 'in', employee_emails),
            ])
        old_users = []
        new_users = []
        users_without_emails = []
        users_with_invalid_emails = []
        users_with_existing_email = []
        for employee in self:
            if employee.user_id:
                old_users.append(employee.name)
                continue
            if not employee.work_email:
                users_without_emails.append(employee.name)
                continue
            if not tools.email_normalize(employee.work_email):
                users_with_invalid_emails.append(employee.name)
                continue
            if email_normalize(employee.work_email) in conflicting_users.mapped('email_normalized'):
                users_with_existing_email.append(employee.name)
                continue
            new_users.append({
                'create_employee_id': employee.id,
                'name': employee.name,
                'phone': employee.work_phone,
                'login': tools.email_normalize(employee.work_email),
                'partner_id': employee.work_contact_id.id,
            })

        next_action = {'type': 'ir.actions.act_window_close'}
        if new_users:
            self.env['res.users'].create(new_users)
            message = _('Users %s creation successful', ', '.join([user['name'] for user in new_users]))
            next_action = _get_user_creation_notification_action(message, 'success', {
                "type": "ir.actions.client",
                "tag": "soft_reload",
                "params": {"next": next_action},
            })

        if old_users:
            message = _('User already exists for Those Employees %s', ', '.join(old_users))
            next_action = _get_user_creation_notification_action(message, 'warning', next_action)

        if users_without_emails:
            message = _("You need to set the work email address for %s", ', '.join(users_without_emails))
            next_action = _get_user_creation_notification_action(message, 'danger', next_action)

        if users_with_invalid_emails:
            message = _("You need to set a valid work email address for %s", ', '.join(users_with_invalid_emails))
            next_action = _get_user_creation_notification_action(message, 'danger', next_action)

        if users_with_existing_email:
            message = _('User already exists with the same email for Employees %s', ', '.join(users_with_existing_email))
            next_action = _get_user_creation_notification_action(message, 'warning', next_action)

        return next_action