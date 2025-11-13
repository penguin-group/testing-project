from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    firstname = fields.Char(
        string="First Name",
        compute="_compute_name_parts",
    )
    lastname = fields.Char(
        string="Last Name",
        compute="_compute_name_parts",
    )

    @api.depends("name")
    def _compute_name_parts(self):
        for partner in self:
            if partner.name:
                parts = partner.name.strip().split()
                if len(parts) > 2:
                    partner.lastname = " ".join(parts[-2:])
                    partner.firstname = " ".join(parts[:-2])
                elif len(parts) == 2:
                    partner.firstname = parts[0]
                    partner.lastname = parts[1]
                else:
                    # If only one word, treat as firstname
                    partner.firstname = parts[0]
                    partner.lastname = ""
            else:
                partner.firstname = ""
                partner.lastname = ""
