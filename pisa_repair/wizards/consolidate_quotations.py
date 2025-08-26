from odoo import models, fields, _
from odoo.exceptions import UserError

class ConsolidateQuotationsWizard(models.TransientModel):
    _name = 'consolidate.quotations.wizard'
    _description = 'Wizard to Consolidate Quotations'

    quotation_ids = fields.Many2many(
        'sale.order', string='Quotations', domain=[('state', '=', 'draft')],
        default=lambda self: self._default_quotations()
    )

    def _default_quotations(self):
        return self.env['sale.order'].browse(self.env.context.get('active_ids', []))

    def action_consolidate_quotations(self):
        if len(self.quotation_ids) < 2:
            raise UserError(_("Please select at least two quotations."))
        

        partner_ids = self.quotation_ids.mapped('partner_id')
        if len(partner_ids) > 1:
            raise UserError(_("All quotations must belong to the same customer."))
        
        error_quotations = []

        for quotation in self.quotation_ids:
            has_repair_order = self.env['repair.order'].search_count([
                ('sale_order_id', '=', quotation.id)
            ])

            if not has_repair_order and not quotation.is_consolidated:
                error_quotations.append(quotation.name)

        if error_quotations:
            raise UserError(_("The following quotations cannot be consolidated because they are not linked to any repair order: %s") % ', '.join(error_quotations))
        
        main_quotation = self.env['sale.order'].create({
            'partner_id': partner_ids[0].id,
            'is_consolidated': True,
            'order_line': [
                (0, 0, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'tax_id': [(6, 0, line.tax_id.ids)],
                    'related_quotation_ids': quotation.id, 
                    'lot_serial': self._get_lot_serial_from_line(line),
                })
                for quotation in self.quotation_ids
                for line in quotation.order_line
            ],
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Consolidated Quotation',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': main_quotation.id,
        }

    def _get_lot_serial_from_line(self, line):

        related_repair_order = self.env['repair.order'].search([
            ('sale_order_id', '=', line.order_id.id)
        ], limit=1) 

        if related_repair_order:
            product = related_repair_order.product_id.display_name
            lot_serial = related_repair_order.lot_id.name if related_repair_order.lot_id else 'No Lot'
            return f"{product} - {lot_serial}"  

        return 'N/A'