from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    github_organization = fields.Char(
        related='company_id.github_organization',
        readonly=False,
        string="GitHub Organization",
        help="The GitHub organization associated with this company.",
    )
    github_token = fields.Char('Github Token')

    def set_values(self):
        super().set_values()
        company_id = self.env.company
        company_id.sudo().write({
            'github_organization': self.github_organization,
            'github_token': self.github_token,
        })

    def get_values(self):
        res = super().get_values()
        res['github_organization'] = self.env.company.github_organization
        res['github_token'] = self.env.company.github_token
        return res
