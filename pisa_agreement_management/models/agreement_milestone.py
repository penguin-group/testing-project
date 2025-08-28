from odoo import fields, models


class AgreementMilestone(models.Model):
    _name = "agreement.milestone"
    _description = "Milestone"

    name = fields.Char("Name", required=True)
    deadline = fields.Date("Deadline", required=True)
    is_reached = fields.Boolean("Is Reached", default=False)
    agreement_id = fields.Many2one("pisa.agreement", string="Related Agreement")
