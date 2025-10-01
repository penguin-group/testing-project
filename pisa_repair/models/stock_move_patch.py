from odoo.addons.repair.models import stock_move as repair_stock_move

repair_stock_move.MAP_REPAIR_LINE_TYPE_TO_MOVE_LOCATIONS_FROM_REPAIR.update({
    'insumo': {
        'location_id': 'location_id',
        'location_dest_id': 'location_dest_id',
    }
})