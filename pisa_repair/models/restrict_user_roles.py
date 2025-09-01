from odoo import models, api, exceptions, _

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.constrains('groups_id')
    def _check_single_custom_role(self):
        role_names = ['Noc', 'Mining', 'Micro', 'Micro Leader']
        for user in self:
            assigned = user.groups_id.filtered(lambda g: g.name in role_names)
            names = assigned.mapped('name')
            if 'Micro Leader' in names and 'Micro' in names:
                names = [n for n in names if n != 'Micro']
            if len(names) > 1:
                raise exceptions.ValidationError(_(
                "A user can only be assigned one role: NOC, MINING o MICRO (o MICRO LEADER). Current: %(roles)s"
            ) % {"roles": ', '.join(sorted(names))})

    @api.model
    def write(self, vals):
        if self.env.context.get('bypass_write', False):
            return super().write(vals)

        res = super().write(vals)

        group_admin = self.env.ref('stock.group_stock_manager', raise_if_not_found=False)
        group_noc = self.env.ref('pisa_repair.group_noc', raise_if_not_found=False)
        group_mining = self.env.ref('pisa_repair.group_mining', raise_if_not_found=False)
        group_micro = self.env.ref('pisa_repair.group_micro', raise_if_not_found=False)
        group_micro_leader = self.env.ref('pisa_repair.group_micro_leader', raise_if_not_found=False)
        group_sales_user = self.env.ref('sales_team.group_sale_salesman', raise_if_not_found=False)

        for user in self:
            groups = user.groups_id

            is_noc = group_noc in groups
            is_micro = group_micro in groups
            is_micro_leader = group_micro_leader in groups
            is_mining = group_mining in groups

            if (is_noc or is_micro_leader) and group_admin and group_admin not in groups:
                user.with_context(bypass_write=True).write({
                    'groups_id': [(4, group_admin.id)]
                })

            if ((is_micro or is_mining) and not is_micro_leader) and group_admin and group_admin in groups:
                user.with_context(bypass_write=True).write({
                    'groups_id': [(3, group_admin.id)]
                })

            if (is_micro or is_micro_leader) and group_sales_user and group_sales_user not in groups:
                user.with_context(bypass_write=True).write({
                    'groups_id': [(4, group_sales_user.id)]
                })

        return res