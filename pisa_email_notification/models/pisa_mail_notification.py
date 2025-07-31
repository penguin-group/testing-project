from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

class PisaMailNotification(models.Model):
    _name = "pisa.mail.notification"
    _description = "Pisa Email Notification"

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
    recipients_filtering_method = fields.Selection(string="Filter users by", selection=[("job_id", "Job Position"), ("employee_id", "Employees")])
    job_ids = fields.Many2many("hr.job", string="Job Positions")
    employee_ids = fields.Many2many("hr.employee", string="Employees")
    definition_type = fields.Selection(
        string="Definition", selection=[("domain", "Domain"), ("formula", "Formula"), ("domain_formula", "Domain & Formula")], default="domain"
    )
    definition_domain = fields.Char()
    python_code = fields.Text(
        string="Python Code",
        help="Write Python code that defines when this rule is applied. "
             "The result of executing the expresion must be "
             "a boolean.",
        default="""# Available locals:\n#  - rec: current record\nTrue""",
    )
    email_custom_message = fields.Text(string="Email Custom Message", required=True)
    active = fields.Boolean(default=True)
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
        ])

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

    def _get_mail_recipients(self):
        self.ensure_one()

        recipient_ids = []
        if self.recipients_filtering_method == 'job_id':
            employees = self.env['hr.employee'].search([('job_id', 'in', self.job_ids.ids)])
            for employee in employees:
                if employee.work_email:
                    recipient_ids.append(employee.user_partner_id.id)
        elif self.recipients_filtering_method == 'employee_id':
            for employee in self.employee_ids:
                if employee.work_email:
                    recipient_ids.append(employee.user_partner_id.id)

        return recipient_ids or False


    def send_notifications(self, record):
        record.message_post(
            body=self.email_custom_message,
            subject=record.name,
            message_type="notification",
            subtype_xmlid="mail.mt_note",
            partner_ids=self._get_mail_recipients(),  # recipient
            email_layout_xmlid="mail.mail_notification_light"
        )
