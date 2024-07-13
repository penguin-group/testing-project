from odoo import models, api, fields, exceptions,_
from odoo.exceptions import UserError,ValidationError

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    price_total = fields.Monetary(required=True)

