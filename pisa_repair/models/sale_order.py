from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_consolidated = fields.Boolean(
        string="Is Consolidated",
        help="Indicates if this quotation is a consolidation of other quotations.",
    )

    has_repair_orders = fields.Boolean(
        string="Has Repair Orders",
        compute="_compute_has_repair_orders",
        store=False
    )

    is_micro_leader = fields.Boolean(
        compute='_compute_is_micro_leader', 
        store=False
    )

    is_only_micro = fields.Boolean(
        compute='_compute_is_only_micro', 
        store=False
    )

    @api.depends()
    def _compute_is_micro_leader(self):
        for order in self:
            order.is_micro_leader = self.env.user.has_group('pisa_repair.group_micro_leader')

    @api.depends()
    def _compute_is_only_micro(self):
        for order in self:
            order.is_only_micro = self.env.user.has_group('pisa_repair.group_micro') and  not self.env.user.has_group('pisa_repair.group_micro_leader')
    
    def _compute_has_repair_orders(self):
        repair_order_model = self.env['repair.order']
        for order in self:
            has_repairs = bool(repair_order_model.search_count([('sale_order_id', '=', order.id)]))
            
            has_related_quotations = any(order.order_line.mapped('related_quotation_ids'))

            order.has_repair_orders = has_repairs or has_related_quotations

            order.is_consolidated = bool(order.is_consolidated)

    @api.model
    def create(self, vals):
        """Intercept the creation of quotations to check consolidations before creating them."""

        if vals.get('is_consolidated', False): 

            # Get the selected sale.orders from the wizard
            sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

            if not sale_orders:
                raise UserError("No quotations have been selected for consolidation.")
            
            parent_consolidated_orders = sale_orders.filtered(lambda so: so.is_consolidated)

            if parent_consolidated_orders:
                error_message = _("Cannot consolidate because one of the selected quotations is already a consolidation and groups other quotations:\n%s") % "\n".join(parent_consolidated_orders.mapped('name'))
                raise UserError(error_message)

            
            already_in_consolidation = self.env['sale.order'].search([
                ('order_line.related_quotation_ids', 'in', sale_orders.ids),
                ('is_consolidated', '=', True),
                ('state', '!=', 'cancel') 
            ])

            if already_in_consolidation:
                consolidation_info = []
                
                for quotation in sale_orders:
                    # Buscar consolidaciones activas a las que pertenece esta cotización
                    related_consolidation = self.env['sale.order.line'].search([
                        ('related_quotation_ids', 'in', [quotation.id])  # Asegurar que sea una lista
                    ]).mapped('order_id.name')
                    
                    if related_consolidation:
                        consolidation_info.append(f"{quotation.name} -> {related_consolidation[0]}")
                
                error_message = _("Cannot consolidate because the following quotations already belong to an active consolidation:\n%s") % "\n".join(consolidation_info)
                raise UserError(error_message)

            # Check if all quotations have products
            invalid_orders = sale_orders.filtered(lambda so: not so.order_line)

            if invalid_orders:
                error_message = _("Cannot consolidate because the following quotations do not have products added:\n%s") % "\n".join(invalid_orders.mapped('name'))
                raise UserError(error_message)

        new_order = super(SaleOrder, self).create(vals)

        return new_order

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)

        if vals.get('state'):
            for order in self:
                # Search for the directly associated repair order
                repair_orders = self.env['repair.order'].search([
                    '|',
                    ('sale_order_id', '=', order.id),  # Repairs linked directly to the consolidation
                    ('sale_order_id', 'in', order.order_line.mapped('related_quotation_ids').ids)  # Repairs of related quotations
                ])

                # Get the quotations (`sale.order_id`) associated with these `repair.order`
                child_sale_orders = repair_orders.mapped('sale_order_id')

                if vals['state'] == 'cancel':
                    for child in child_sale_orders:
                        if child.state != 'draft':
                            with self.env.cr.savepoint():
                                child.with_context(tracking_disable=True).write({'state': 'draft'})
                else:
                    for child in child_sale_orders:
                        if child.state != vals['state']:
                            with self.env.cr.savepoint():
                                child.with_context(tracking_disable=True).write({'state': vals['state']})

                if repair_orders:                        
                    # Get the necessary tags
                    tags = {tag.name: tag for tag in self.env['repair.tags'].search([
                        ('name', 'in', ['Quotation Created', 'Quotation Sent', 'Not Approved', 'Approved'])
                    ])}

                    # Define tag transitions based on the consolidation state
                    tag_transitions = {
                        'sent': {
                            'add': ['Quotation Sent'],
                            'remove': ['Quotation Created', 'Approved', 'Not Approved']
                        },
                        'sale': {
                            'add': ['Approved'],
                            'remove': ['Quotation Sent', 'Quotation Created', 'Not Approved']
                        },
                        'cancel': {
                            'add': ['Not Approved'],
                            'remove': ['Quotation Sent', 'Quotation Created', 'Approved']
                        }
                    }

                    # Apply changes based on the new state
                    changes = tag_transitions.get(vals.get('state'), {})

                    remove_tags = [tags[tag] for tag in changes.get('remove', []) if tag in tags]
                    add_tags = [tags[tag] for tag in changes.get('add', []) if tag in tags]

                    for repair_order in repair_orders:
                        # Get only the tags that will be removed
                        removed_tag_names = ', '.join(tag.name for tag in remove_tags if tag in repair_order.tag_ids) or "No tags"

                        # Remove tags if they exist
                        if remove_tags:
                            repair_order.write({'tag_ids': [(3, tag.id) for tag in remove_tags]})

                        if add_tags:
                            for tag in add_tags:
                                # Save in the change history
                                self.env['repair.order.tag.history'].create({
                                    'repair_order_id': repair_order.id,
                                    'tag_id': tag.id,
                                    'user_id': self.env.user.id,
                                })

                                # Build message and post it (only show the removed ones)
                                message = f"{removed_tag_names} ➞ {tag.name} / Tags"
                                repair_order.message_post(
                                    body=message,
                                    author_id=self.env.user.partner_id.id,
                                    subtype_xmlid="mail.mt_note"
                                )

                        # Add tags in a single operation
                        repair_order.write({'tag_ids': [(4, tag.id) for tag in add_tags]})
        return res
    
    def action_draft(self):
        """Restore 'Quotation Created' tag and remove 'Not Approved' when resetting the sale order to draft."""
        res = super(SaleOrder, self).action_draft()

        for order in self:
            repair_orders = self.env['repair.order'].search([
                '|',
                ('sale_order_id', '=', order.id),  # Repairs linked directly to the consolidation
                ('sale_order_id', 'in', order.order_line.mapped('related_quotation_ids').ids)  # Repairs of related quotations
            ])

            if not repair_orders:
                continue
            
            # Get the necessary tags
            tags = {tag.name: tag for tag in self.env['repair.tags'].search([
                ('name', 'in', ['Quotation Created', 'Not Approved'])
            ])}

            for repair_order in repair_orders:
                removed_tag_names = ""
                added_tag_names = ""

                # Remove 'Not Approved' if present in the order
                if 'Not Approved' in tags and tags['Not Approved'] in repair_order.tag_ids:
                    repair_order.write({'tag_ids': [(3, tags['Not Approved'].id)]})
                    removed_tag_names = tags['Not Approved'].name

                # Add 'Quotation Created' if not present
                if 'Quotation Created' in tags and tags['Quotation Created'] not in repair_order.tag_ids:
                    repair_order.write({'tag_ids': [(4, tags['Quotation Created'].id)]})
                    added_tag_names = tags['Quotation Created'].name

                # Post message if there were changes
                if removed_tag_names or added_tag_names:
                    message = f"{removed_tag_names} ➞ {added_tag_names} / Tags"
                    repair_order.message_post(
                        body=message,
                        author_id=self.env.user.partner_id.id,
                        subtype_xmlid="mail.mt_note"
                    )

        return res
    
    def action_quotation_send(self):

        for order in self:
            if order.is_only_micro:
                raise UserError(_("You do not have sufficient permissions"))
            
        res = super(SaleOrder, self).action_quotation_send()

        for order in self:
            res['context'].update({
                'default_model': 'sale.order',
                'default_res_ids': [order.id],
            })
        return res
    
    def action_confirm(self):
        """Confirm the consolidation only if all quotations have products."""

        for order in self:
            if order.is_only_micro:
                raise UserError(_("You do not have sufficient permissions"))

        res = super(SaleOrder, self).action_confirm()

        for order in self:
            for line in order.order_line:
                for quotation in line.related_quotation_ids:
                    if quotation.state not in ['sale', 'cancel']:
                        quotation.action_confirm()

        return res