from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = 'stock.move'

    repair_line_type = fields.Selection(selection_add=[('insumo', 'Insumo')])

    @api.model_create_multi
    def create(self, vals_list):
        """Extends Odoo functionality to process movements of type 'Insumo'."""
        
        for vals in vals_list:
            if vals.get('repair_line_type', '') == 'insumo':
                
                product_id = vals.get('product_id')

                if not product_id:
                    raise ValueError("Error: No valid product provided.")

                src_location = self.env['stock.quant'].search([
                    ('product_id', '=', product_id),
                    ('quantity', '>', 0),
                    ('location_id.usage', '=', 'internal'),
                    ('location_id.scrap_location', '=', False)
                ], order='id asc', limit=1).location_id

                if not src_location:
                    raise ValueError(_("Error: No internal location found for the product %s.") % product_id)

                scrap_location = self.env['stock.location'].search([('scrap_location', '=', True)], limit=1)

                if not scrap_location:
                    raise ValueError(_("Error: No valid Scrap location found in the database."))

                vals.update({
                    'location_id': src_location.id,
                    'location_dest_id': scrap_location.id,
                    'state': 'done'
                })

        moves = super(StockMove, self).create(vals_list)

        for move in moves:
            if move.repair_line_type == 'insumo':
                if not move.location_id:
                    move.write({'location_id': src_location.id})
                
                if not move.location_dest_id:
                    move.write({'location_dest_id': scrap_location.id})

                move._action_done()

        return moves
    
    def write(self, vals):
        """Extends Odoo functionality to validate stock availability on update."""
        
        if 'quantity' in vals:
            product_ids = self.mapped('product_id').ids

            if product_ids:
                stock_data = self.env['stock.quant'].read_group(
                    domain=[
                        ('product_id', 'in', product_ids),
                        ('quantity', '>', 0),
                        ('location_id.usage', '=', 'internal')
                    ],
                    fields=['product_id', 'quantity:sum'],
                    groupby=['product_id']
                )

                stock_dict = {data['product_id'][0]: data['quantity'] for data in stock_data}

                for record in self:
                    new_quantity = vals.get('quantity', record.quantity)
                    total_stock = stock_dict.get(record.product_id.id, 0)

                    if total_stock == 0:
                        raise UserError(_("Warning: No availability of product %s in any warehouse.") % record.product_id.display_name)

                    if new_quantity > total_stock:
                        raise UserError(_("Warning: The requested quantity (%s) of product %s exceeds the available stock (%s).") % (new_quantity, record.product_id.display_name, total_stock))

        return super().write(vals)
