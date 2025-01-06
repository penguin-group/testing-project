import logging
from odoo import api, fields, models, _
from odoo.tools import index_exists
from odoo.exceptions import ValidationError, UserError
import hashlib
import qrcode
from io import BytesIO
import base64
import re
import math

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'   
    def action_invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can more easily see the next step of the workflow. """
        if any(not move.is_invoice(include_receipts=True) for move in self):
            raise UserError(_("Only invoices can be printed"))
        self.filtered(lambda inv: not inv.action_invoice_sent).write({'mark_invoice_as_sent': True})
        return self.env.ref('l10n_py_selfprinted_invoice.invoice_report_action2').report_action(self)
