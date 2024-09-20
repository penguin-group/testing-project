from odoo import fields, api, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    invoice_authorization_id = fields.Many2one(
        'invoice.authorization', 
        string='Invoice Authorization',
        domain="[('document_type', 'in', ['out_invoice', 'out_refund'])]"
    )
    max_lines = fields.Integer(
        string="Maximum printable lines on the invoice",
        default=0,
        help="0 for unlimited lines."
    )
    invoice_footer = fields.Html(string="Invoice Footer")
    show_qr = fields.Boolean(string="Show QR in self-printed invoices")
