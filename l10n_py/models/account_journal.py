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
    res90_type_receipt = fields.Selection([('101', 'Self-invoicing'),
                                               ('102', 'Public Passenger Transport Ticket'),
                                               ('103', 'Sales Invoice'),
                                               ('104', 'Resimple ticket'),
                                               ('105', 'Lottery Tickets, Games of Chance'),
                                               ('106', 'Ticket or air transportation ticket'),
                                               ('107', 'Import clearance'),
                                               ('108', 'Entrance to public shows'),
                                               ('109', 'Bill'),
                                               ('110', 'Credit note'),
                                               ('111', 'Debit note'),
                                               ('112', 'Cash register machine ticket'),
                                               ('201', 'Proof of expenses for credit purchases'),
                                               ('202', 'Legalized proof of foreign residence'),
                                               ('203', 'Proof of income from credit sales'),
                                               ('204', 'Proof of income from Public, Religious or Public Benefit Entities'),
                                               ('205', 'Account statement - Electronic ticketing'),
                                               ('206', 'Account statement - IPS'),
                                               ('207', 'Account statement - TC/TD'),
                                               ('208', 'Salary Settlement'),
                                               ('209', 'Other expenditure vouchers'),
                                               ('210', 'Other proof of income'),
                                               ('211', 'Bank transfers or money orders / Deposit slip'),
                                               ])
    res90_imputes_irp_rsp_default = fields.Boolean(string="Impute IRP/RSP by default")
    exclude_res90=fields.Boolean(string="Exclude from Resolution 90",copy=False,help="The records of this journal will not be included in resolution 90")

    @api.onchange('type')
    @api.depends('type')
    def assign_voucher_type(self):
        for i in self:
            if i.type in ['sale','purchase']:
                i.res90_type_receipt='109'
            else:
                i.res90_type_receipt=None
