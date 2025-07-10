from odoo import api, fields, models

class POMailNotification(models.Model):
    _name = "po.mail.notification"
    _description = "Purchase Order Mail Notification"

    @api.model
    def _get_default_name(self):
        return self.env._("New Notification")

    name = fields.Char(
        string="Description",
        required=True,
        default=lambda self: self._get_default_name(),
        translate=True,
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
    )
    model = fields.Char(related="model_id.model", index=True, store=True)
    employee_ids = fields.Many2many("hr.employee", string="Employees" )
    definition_type = fields.Selection(
        string="Definition", selection=[("domain", "Domain")], default="domain"
    )
    definition_domain = fields.Char()
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=30)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

