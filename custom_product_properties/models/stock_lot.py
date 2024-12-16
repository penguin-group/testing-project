from odoo import models, fields

class StockLot(models.Model):
    _inherit = 'stock.lot'

    customer = fields.Char(string='Customer', help="Name of the customer associated with the batch.")
    container = fields.Char(string='Container', help="Identifier of the associated container.")
    miner_waranty_expiration_date = fields.Date(string='Miner Warranty Expiration Date', help="Miner's warranty expiration date.")
    status = fields.Boolean(string='Status', help="Indicates the status of the miner")
