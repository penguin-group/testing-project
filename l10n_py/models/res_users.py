from odoo import models, api, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def add_users_to_l10n_py_security_group(self):
        target_country_codes = ['PY']
        group = self.env.ref('l10n_py.l10n_py_security_group')

        match_user_ids = []
        all_users = self.sudo().search([])
        pry_companies = self.env['res.company'].sudo().search([]).filtered(lambda c: c.country_id.code == 'PY')
        
        for company in pry_companies:
            match_user_ids += all_users.filtered(lambda user: company.id in user.company_ids.mapped('id')).ids

        match_user_ids = list(set(match_user_ids))
        for user in self.sudo().browse(match_user_ids):
            if group not in user.groups_id:
                user.groups_id = [(4, group.id)]
