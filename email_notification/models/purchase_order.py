from odoo import api, models
from odoo.tools import formatLang


class PisaMailNotification(models.Model):
    _inherit = "pisa.mail.notification"

    @api.model
    def _get_email_notification_model_names(self):
        res = super()._get_email_notification_model_names()
        res.append("purchase.order")
        return res

    def send_notifications(self, record):
        if self.model_id.model != 'purchase.order':
            return False

        template = super(PisaMailNotification, self).send_notifications(record)

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        route_url = f'/odoo/purchase/{record.id}/'
        record_url = f"{base_url}{route_url}"

        amount_in_usd = ''  # symbol + amount
        if record.currency_id.name == 'USD':
            amount_in_usd = formatLang(self.env, record.amount_total, currency_obj=self.company_currency_id)
        else:
            amount_in_usd = record.tax_totals['amount_total_cc'].removeprefix('(').removesuffix(')')

        email_custom_values = {'amount_in_usd': amount_in_usd, 'record_url': record_url}

        template.with_context(email_custom_values).send_mail(record.id, force_send=True)

        return template

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