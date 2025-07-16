from odoo import api, models


class MailNotification(models.Model):
    _inherit = "pisa.mail.notification"

    @api.model
    def _get_email_notification_model_names(self):
        res = super()._get_email_notification_model_names()
        res.append("purchase.order")
        return res


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super().button_confirm()

        for po in self:
            rules = self.env['pisa.mail.notification'].get_applicable_mail_notification_rules(po._name)
            for rule in rules:
                if rule.check_mail_notification_rule(po):
                    rule.send_notifications(po)
        return res