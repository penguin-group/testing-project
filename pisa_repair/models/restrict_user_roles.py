from odoo import models, api, exceptions

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.constrains('groups_id')
    def _check_single_custom_role(self):
        role_names = ['Noc', 'Mining', 'Micro']
        for user in self:
            assigned_roles = user.groups_id.filtered(lambda g: g.name in role_names)
            if len(assigned_roles) > 1:
                raise exceptions.ValidationError(
                    "A user can only be assigned one role: NOC, MINING, or MICRO. "
                    f"Currently assigned roles: {', '.join(assigned_roles.mapped('name'))}"
                )

    @api.model
    def write(self, vals):
        if self.env.context.get('bypass_write', False):
            return super().write(vals)

        res = super().write(vals)

        group_admin = self.env.ref('stock.group_stock_manager', raise_if_not_found=False)
        group_noc = self.env.ref('pisa_repair.group_noc', raise_if_not_found=False)
        group_mining = self.env.ref('pisa_repair.group_mining', raise_if_not_found=False)
        group_micro = self.env.ref('pisa_repair.group_micro', raise_if_not_found=False)

        for user in self:
            groups = user.groups_id

            is_noc = group_noc in groups
            is_micro = group_micro in groups
            is_mining = group_mining in groups

            if is_noc and group_admin not in groups:
                user.with_context(bypass_write=True).write({
                    'groups_id': [(4, group_admin.id)]
                })

            if (is_micro or is_mining) and group_admin in groups:
                user.with_context(bypass_write=True).write({
                    'groups_id': [(3, group_admin.id)]
                })

        return res