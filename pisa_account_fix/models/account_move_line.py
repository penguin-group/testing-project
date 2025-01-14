from odoo import models
from odoo.exceptions import UserError

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

