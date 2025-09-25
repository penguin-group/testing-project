from odoo import models, api

class RepairOrderComputes(models.Model):
    _inherit = 'repair.order'

    @api.depends('state')
    def _compute_show_next_button(self):
        for record in self:
            record.show_next_button = record.state not in ['done', 'cancel']

    @api.depends_context('is_validated_temp')
    def _compute_is_validated(self):
        for record in self:
            record.is_validated = self.env.context.get('is_validated_temp', False)

    @api.depends('state')
    def _compute_is_validated(self):
        for record in self:
            if not record.id and self.env.user.has_group('pisa_repair.group_noc'):
                record.is_validated = True
            elif self.env.user.has_group('pisa_repair.group_noc') and record.state == 'draft':
                record.is_validated = True
            elif not record.id and self.env.user.has_group('pisa_repair.group_mining'):
                record.is_validated = False
                record.is_mining = False
            else:
                record.is_validated = self.env.context.get('is_validated_temp', False)

    @api.depends('state')
    def _compute_is_noc(self):
        for order in self:
            order.is_noc = self.env.user.has_group('pisa_repair.group_noc')

    @api.depends('state')
    def _compute_is_mining(self):
        for order in self:
            order.is_mining = self.env.user.has_group('pisa_repair.group_mining')

    @api.depends('state')
    def _compute_is_micro(self):
        for order in self:
            order.is_micro = self.env.user.has_group('pisa_repair.group_micro')

    @api.depends('state')
    def _compute_is_inventory_admin(self):
        for order in self:
            order.is_inventory_admin = self.env.user.has_group('stock.group_stock_manager')

    @api.depends('state')
    def _compute_is_inventory_user(self):
        for order in self:
            order.is_inventory_user = self.env.user.has_group('stock.group_stock_user')