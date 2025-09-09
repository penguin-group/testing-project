from odoo import models, fields, api, _


class RepairOrderFields(models.Model):
    _inherit = 'repair.order'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=False)

    lot_id = fields.Many2one('stock.lot', string="Lot/Serial Number")

    scrapped = fields.Boolean(string="Is the product scrapped?", default=False)

    is_validated = fields.Boolean(
        string="Is Validated",
        compute="_compute_is_validated",
        store=False,
        readonly=True
    )

    is_noc = fields.Boolean(
        string="Is NOC",
        compute='_compute_is_noc', 
        store=False
    )

    is_mining = fields.Boolean(
        string="Is MINING",
        compute='_compute_is_mining', 
        store=False
    )

    is_inventory_admin = fields.Boolean(
        string="Is Inventory Admin",
        compute='_compute_is_inventory_admin',
        store=False
    )

    is_inventory_user = fields.Boolean(
        string="Is Inventory User",
        compute='_compute_is_inventory_user',
        store=False
    )

    is_micro = fields.Boolean(
        string="Is MICRO",
        compute='_compute_is_micro', 
        store=False
    )

    donated_component_ids = fields.One2many(
        "repair.donated.component",
        "ticket_origin_id",
        string="Donated Components"
    )

    consumed_component_ids = fields.One2many(
        "repair.consumed.component",
        "repair_order_id",
        string="Consumed Components"
    )

    has_donor_tag = fields.Boolean(
        compute="_compute_has_donor_tag",
        store=False
    )
           
    tag_names = fields.Char(compute='_compute_tag_names', store=False)

    
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product to Repair',
        required=True,
        domain="[('is_miner_category', '=', True)]"
    )

    sequence = fields.Integer(string="Sequence", default=10)

    state = fields.Selection(
        selection_add=[
            ('draft', _("Open Tickets")),
            ('confirmed', _("In Progress")),
            ('under_repair', _("Repair Service Stage")),
            ('ready_for_deployment', _("Ready For Deployment")),
            ('done', _("Done")),
            ('cancel', _("Cancelled")),
        ],
        default='draft',
        string='Status',
        tracking=True,
        index=True
    )

    show_next_button = fields.Boolean(
        string="Show Next Button", compute="_compute_show_next_button", store=True
    )

    lot_ref = fields.Char(
        string="Internal Reference",
        related='lot_id.ref',
        store=False,
    )

    lot_display = fields.Char(
        compute="_compute_lot_display",
        store=False
    )

    state_priority = fields.Integer(
        string="State Priority",
        compute="_compute_state_priority",
        store=True
    )

    external_service_id = fields.Many2one(
        'repair.external.service',
        string="External Service",
        ondelete='restrict'
    )

    def write(self, vals):
        res = super().write(vals)

        if self.env.context.get("skip_update_donor_scrapped_tags"):
            return res

        # Si se consumió un componente donado desde otro ticket
        consumed_lines = vals.get("consumed_component_ids", [])
        for cmd in consumed_lines:
            if len(cmd) >= 3 and "donated_component_id" in cmd[2]:
                donated_comp = self.env["repair.donated.component"].browse(cmd[2]["donated_component_id"])
                if donated_comp and donated_comp.ticket_origin_id:
                    origin_order = donated_comp.ticket_origin_id
                    origin_order.with_context(skip_update_donor_scrapped_tags=True)._update_donor_scrapped_tags()

        # Además, seguimos revisando el propio ticket en caso de ser origen
        for order in self:
            order.with_context(skip_update_donor_scrapped_tags=True)._update_donor_scrapped_tags()

        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super(RepairOrderFields, self).create(vals_list)

        open_tag = self.env.ref('pisa_repair.open', raise_if_not_found=False)
        if open_tag:
            for record in records:
                record.write({'tag_ids': [(4, open_tag.id)]})

        return records

    @api.depends('state')
    def _compute_state_priority(self):
        state_order = {
            'draft': 1,
            'confirmed': 2,
            'under_repair': 3,
            'ready_for_deployment': 4,
            'done': 5,
            'cancel': 6,
        }
        for record in self:
            record.state_priority = state_order.get(record.state, 100)
            

    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        groups = super(RepairOrderFields, self).read_group(domain, fields, groupby, offset, limit, orderby, lazy)

        state_order = {
            'draft': 1,
            'confirmed': 2,
            'under_repair': 3,
            'ready_for_deployment': 4,
            'done': 5,
            'cancel': 6,
        }

        if 'state' in groupby:
            groups.sort(key=lambda g: state_order.get(g.get('state'), 100))

        return groups

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        if self.lot_id:
            self._set_partner_from_lot()
            return self._validate_unique_repair_order()
        else:
            self.partner_id = False
    
    @api.depends('tag_ids')
    def _compute_tag_names(self):
        for record in self:
            record.tag_names = ','.join(record.tag_ids.mapped('name')).lower()
    

    def _set_partner_from_lot(self):
        """ Searches and assigns the customer based on the serial number (lot_id). """
        customer_name = self.lot_id.customer if self.lot_id.customer else None
        if customer_name:
            customer_record = self.env['res.partner'].search([('name', 'ilike', customer_name)], limit=1)
            self.partner_id = customer_record.id if customer_record else False
        else:
            self.partner_id = False

    def _validate_unique_repair_order(self):
        """ Checks if there is already an active ticket with the same serial number. """
        existing_ticket = self.env['repair.order'].search([
            ('lot_id', '=', self.lot_id.id),
            ('state', 'not in', ['done', 'cancel']),
            ('id', '!=', self.id)
        ], limit=1)

        if existing_ticket:
            self.lot_id = False
            return {
                'warning': {
                    'title': _("Validation Error"),
                    'message': _("The product with serial number [%s] already has an active repair ticket ([%s]). It must be completed before creating a new ticket.") % (existing_ticket.lot_id.name, existing_ticket.name)
                }
            }
        
        scrapped_order = self.env['repair.order'].search([
            ('lot_id', '=', self.lot_id.id),
            ('scrapped', '=', True),
        ], limit=1)

        if scrapped_order:
            self.lot_id = False
            return {
                'warning': {
                    'title': _("Validation Error"),
                    'message': _("The product with serial number [%s] was previously marked as irreparable in repair order [%s]. It cannot be added to a new repair order.") % (scrapped_order.lot_id.name, scrapped_order.name)
                }
            }

    def _compute_lot_display(self):
        for record in self:
            if record.lot_id:
                lot_name = record.lot_id.name
                record.lot_display = '*' * 10 + lot_name[10:] if len(lot_name) > 10 else '*' * len(lot_name)
                
            else:
                record.lot_display = ''

    def _compute_has_donor_tag(self):
        donor_tag = self.env.ref("pisa_repair.donor", raise_if_not_found=False)
        for record in self:
            record.has_donor_tag = donor_tag in record.tag_ids if donor_tag else False

    def _update_donor_scrapped_tags(self):
        scrapped_tag = self.env.ref("pisa_repair.scrapped", raise_if_not_found=False)
        donor_tag = self.env.ref("pisa_repair.donor", raise_if_not_found=False)

        for order in self:
            if not order.donated_component_ids:
                continue

            all_used = all(comp.used for comp in order.donated_component_ids)
          

            if all_used:
                if scrapped_tag and scrapped_tag not in order.tag_ids:
                    order.with_context(skip_update_donor_scrapped_tags=True).write({
                        "tag_ids": [(4, scrapped_tag.id)]
                    })
                if donor_tag and donor_tag in order.tag_ids:
                    order.with_context(skip_update_donor_scrapped_tags=True).write({
                        "tag_ids": [(3, donor_tag.id)]
                    })
            else:
                if donor_tag and donor_tag not in order.tag_ids:
                    order.with_context(skip_update_donor_scrapped_tags=True).write({
                        "tag_ids": [(4, donor_tag.id)]
                    })
                if scrapped_tag and scrapped_tag in order.tag_ids:
                    order.with_context(skip_update_donor_scrapped_tags=True).write({
                        "tag_ids": [(3, scrapped_tag.id)]
                    })