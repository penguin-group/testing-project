from odoo import models, api, fields, _
from datetime import datetime
from odoo.tools.misc import format_date
import logging

_logger = logging.getLogger(__name__)

class Agreement(models.Model):
    _name = 'agreement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Agreement'
    _order = 'sequence, id'

    def _default_stage_id(self):
        # Stages are ordered by sequence first.
        # In a kanban view, for example, the lower the sequence of the stage,
        # the further to the left it is going to be.
        stage = self.env['agreement.stage'].search([('active', '=', True)], order="sequence", limit=1).id
        return stage if stage else False

    name = fields.Char(string="Agreement Name", required=True, default="New Agreement", tracking=True)
    partner_ids = fields.Many2many('res.partner', string="Partner", required=False, tracking=True)
    signature_date = fields.Date(string="Signature Date", required=False, tracking=True)
    start_date = fields.Date(string="Start Date", required=False, tracking=True)
    end_date = fields.Date(string="End Date", required=False, tracking=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, required=False)
    stage_id = fields.Many2one("agreement.stage",
                               string="Stage",
                               ondelete='restrict',  # Restrict the deletion of a record if a stage is related to it
                               copy=False,
                               index=True,
                               tracking=True,
                               default=_default_stage_id,
                               required=True,
                               group_expand='_read_group_expand_full'  # Always display all stages even if some of them have no records (!)
    )
    sequence = fields.Integer(default=10)
    key_obligations = fields.Text(string="Key Obligations", tracking=True)
    active = fields.Boolean(default=True)
    code = fields.Char(string="Code", tracking=True)

    agreement_type = fields.Many2one('agreement.type', string="Agreement Type", tracking=True)
    legal_process_type = fields.Many2one('agreement.legal.process.type', string="Legal Process Type", tracking=True)
    renewal_terms = fields.Many2one("agreement.renewal.term", string="Renewal Terms", tracking=True)
    jurisdiction = fields.Many2one("agreement.jurisdiction", string="Jurisdiction", tracking=True)
    tag_ids = fields.One2many("agreement.tag", "agreement_id", string="Agreement Tag")
    related_agreements = fields.Many2many(
        'agreement',
        'agreement_rel',
        'agreement_id',
        'related_agreement_id',
        string="Related Agreements",
        help="Agreements that are related to this one",
        tracking=True
    )
    file_location = fields.Char(string="File Location (URL)", tracking=True)
    milestone_ids = fields.One2many('agreement.milestone', "agreement_id", string="Milestone", tracking=True)

    def retrieve_partners_to_be_notified(self, agreement):
        """Checks access groups and agreement following and returns all the relevant users to send the notification to."""
        partners = []
        agreement_legal_officers = self.env.ref('agreement.group_agreement_legal_officer', raise_if_not_found=True).users
        agreement_admins = self.env.ref('agreement.group_agreement_admin', raise_if_not_found=True).users
        allowed_users = [*agreement_admins, *agreement_legal_officers]

        for user in allowed_users:
            if user.partner_id:
                partners.append(user.partner_id.id)

        partners += agreement.message_partner_ids.ids  # followers of the agreement
        partners = list(set(partners))  # remove any duplicate ids
        return partners

    def check_agreement_approaching_dates(self):
        """Method called by a cron job which compares today's date
        with the agreement's end_date and its milestones' deadline.
        If the conditions are met, calls the send_email_notification method to notify the user.
        """
        notify_ten_days_prior = bool(self.env['ir.config_parameter'].get_param("res_config_settings.notify_ten_days_prior"))
        notify_one_day_prior = bool(self.env['ir.config_parameter'].get_param("res_config_settings.notify_one_day_prior"))
        notify_on_the_date = bool(self.env['ir.config_parameter'].get_param("res_config_settings.notify_on_the_date"))
        today = datetime.today().date()
        agreements = self.env['agreement'].search([])

        for agreement in agreements:
            if not agreement.end_date:
                continue

            amount_of_days_before_end_date = (today - agreement.end_date).days
            if ((amount_of_days_before_end_date == 0 and notify_on_the_date) or
                (amount_of_days_before_end_date == -1 and notify_one_day_prior) or
                (amount_of_days_before_end_date == -10 and notify_ten_days_prior)):
                partner_ids = self.retrieve_partners_to_be_notified(agreement)
                self.send_email_notification(agreement,
                                             amount_of_days_before_end_date,
                                             'agreement.mail_template_notification_agreement',
                                             partner_ids)

            for milestone in agreement.milestone_ids:
                if not milestone.deadline:
                    continue

                amount_of_days_before_deadline = (today - milestone.deadline).days
                if ((amount_of_days_before_deadline == 0 and notify_on_the_date) or
                        (amount_of_days_before_deadline == -1 and notify_one_day_prior) or
                        (amount_of_days_before_deadline == -10 and notify_ten_days_prior)):
                    # agreement.milestone doesn't have followers. Notifications related to
                    # a milestone's deadline are sent to the agreement followers.
                    partner_ids = self.retrieve_partners_to_be_notified(agreement)
                    self.send_email_notification(milestone,
                                                 amount_of_days_before_deadline,
                                                 'agreement.mail_template_notification_milestone',
                                                 partner_ids)

    def send_email_notification(self, record, amount_of_days_before_end_date, template_id, partner_ids):
        """Sends an email notification to the relevant users (chosen based on access groups and following)."""
        template = self.env.ref(template_id)

        match amount_of_days_before_end_date:  # Customize subject depending on model of record and amount of days left
            case -10:
                template.subject = f"{_('Milestone') if record._name == 'agreement.milestone' else _('Agreement')} {record.name} {_('ends in') + " " + str(abs(amount_of_days_before_end_date)) + " " + _('days.')}"
            case -1:
                template.subject = f"{_('Milestone') if record._name == 'agreement.milestone' else _('Agreement')} {record.name} ends tomorrow."
            case 0:
                template.subject = f"{_('Milestone') if record._name == 'agreement.milestone' else _('Agreement')} {record.name} ends today."


        partners = self.env['res.partner'].browse(partner_ids)
        for partner in partners:
            template.lang = partner.lang
            if partner.email:
                final_date = record.end_date if 'end_date' in record else record.deadline
                date_str = format_date(self.env, final_date, date_format='long', lang_code=partner.lang)
                template.with_context(date_str=date_str).send_mail(record.id,
                                                                   email_layout_xmlid="mail.mail_notification_light",
                                                                   email_values={'email_to': partner.email},
                                                                   force_send=True)
            else:
                _logger.warning(f"{partner.name} does not have an email address. Notification not sent for agreement with ID {record.id}.")



