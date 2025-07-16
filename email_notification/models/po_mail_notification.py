from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.osv import expression
from odoo.tools import formatLang

class PisaMailNotification(models.Model):
    _name = "pisa.mail.notification"
    _description = "Email Notification"

    @api.model
    def _get_default_name(self):
        return self.env._("New Mail Notification Rule")

    @api.model
    def _get_email_notification_model_names(self):
        res = []
        return res

    name = fields.Char(
        string="Description",
        required=True,
        default=lambda self: self._get_default_name(),
        translate=True,
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        domain=lambda self: [("model", "in", self._get_email_notification_model_names())]
    )
    model = fields.Char(related="model_id.model", index=True, store=True)
    receiver_filtering_method = fields.Selection(string="Filter users by", selection=[("job_id", "Job Position"), ("employee_id", "Employees")])
    job_ids = fields.Many2many("hr.job", string="Job Positions")
    employee_ids = fields.Many2many("hr.employee", string="Employees")
    definition_type = fields.Selection(
        string="Definition", selection=[("domain", "Domain"), ("formula", "Formula"), ("domain_formula", "Domain & Formula")], default="domain"
    )
    definition_domain = fields.Char()
    python_code = fields.Text(
        string="Tier Definition Expression",
        help="Write Python code that defines when this rule is applied. "
             "The result of executing the expresion must be "
             "a boolean.",
        default="""# Available locals:\n#  - rec: current record\nTrue""",
    )
    template_id = fields.Many2one(
        "mail.template",
        string="Email Template",
        domain="[('model_id', '=', model_id)]",
        help="Template used for the email notification.",
    )
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=30)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    @api.model
    def get_applicable_mail_notification_rules(self, model_name):
        """Return all active rules for this model."""
        return self.search([
            ('model', '=', model_name),
            ('active', '=', True),
            ('company_id', 'in', [self.env.company.id, False]),
        ], order='sequence')

    def check_mail_notification_rule(self, record):
        """Evaluate the rule’s domain or Python code against a single record. Returns True if it matches."""
        self.ensure_one()
        if self.definition_type == 'domain' and self.definition_domain:
            domain = safe_eval(self.definition_domain, {'env': self.env, 'user': self.env.user})  # evaluate the domain string into a Python list

            # return if this record meets the domain criteria
            return bool(self.env[self.model].search_count([('id', '=', record.id)] + domain))

        elif self.definition_type == "formula":
            code_evaluation_result = safe_eval(self.python_code, globals_dict={"rec": record})
            return code_evaluation_result  # True or False

        elif self.definition_type == "domain_formula" and self.definition_domain:
            domain = safe_eval(self.definition_domain, {'env': self.env, 'user': self.env.user})
            dom_evaluation_result = bool(self.env[self.model].search_count([('id', '=', record.id)] + domain))
            code_evaluation_result = safe_eval(self.python_code, globals_dict={"rec": record})

            return bool(dom_evaluation_result and code_evaluation_result)

        return False

    def send_notifications(self, record):
        self.ensure_one()

        template = self.env.ref('email_notification.mail_template_notification_po')

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        route_url = f'/odoo/purchase/{record.id}/'
        record_url = f"{base_url}{route_url}"

        amount_in_usd = ''  # symbol + amount
        if record.currency_id.name == 'USD':
            amount_in_usd = formatLang(self.env, record.amount_total, currency_obj=self.company_currency_id)
        else:
            amount_in_usd = record.tax_totals['amount_total_cc'].removeprefix('(').removesuffix(')')

        email_custom_values = {'employee_name': ceo.name, 'amount_in_usd': amount_in_usd, 'record_url': record_url}

        template.with_context(email_custom_values).send_mail(
            record.id,
            force_send=True,
            email_values={'email_to': ceo.work_email},
        )


        print("notification sent!")