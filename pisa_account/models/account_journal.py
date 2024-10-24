from odoo import fields, models

class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    payment_info = fields.Html(
        string="Payment info", 
        help="Payment info for customers. This data will appear in the QR code of the self-printed invoice."
    )
    local_suppliers = fields.Boolean(string="Local Suppliers")