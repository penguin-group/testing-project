from odoo import models, api, fields


AGREEMENT_STAGES = [
    ('draft', 'Draft'),
    ('missing_info', 'Missing Information'),
    ('under_review', 'Under Review'),
    ('executed', 'Executed'),
    ('active', 'Active'),
    ('expired', 'Expired'),
    ('terminated', 'Terminated')
]


class PisaAgreement(models.Model):
    _name = 'pisa.agreement'

    name = fields.Char(string="Agreement Name", required=True)
    partner_id = fields.Many2one('res.partner', string="Partner", required=False)
    signature_date = fields.Date(string="Signature Date", required=False)
    start_date = fields.Date(string="Start Date", required=False)
    end_date = fields.Date(string="End Date", required=False)
    company_id = fields.Many2one('res.company', string="Company", required=False)
    stage = fields.Selection(AGREEMENT_STAGES, string="Stage", default='draft')
    key_obligations = fields.Text(string="Key Obligations")

    agreement_type = fields.Many2one('agreement.type', string="Agreement Type")
    legal_process_type = fields.Many2one('legal.process.type', string="Legal Process Type")

    related_agreements = fields.Many2many(
        'pisa.agreement',
        'pisa_agreement_rel',
        'agreement_id',
        'related_agreement_id',
        string="Related Agreements",
        help="Agreements that are related to this one"
    )
