from odoo import models, api, fields


class PisaAgreement(models.Model):
    _name = 'pisa.agreement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Agreement'
    _order = 'sequence, id'

    def _default_stage_id(self):
        # Stages are ordered by sequence first.
        # In a kanban view, for example, the lower the sequence of the stage,
        # the further to the left it is going to be.
        stage = self.env['agreement.stage'].search([('active', '=', True)], order="sequence", limit=1).id
        return stage if stage else False

    name = fields.Char(string="Agreement Name", required=True, default="New Agreement")
    partner_ids = fields.Many2many('res.partner', string="Partner", required=False)
    signature_date = fields.Date(string="Signature Date", required=False)
    start_date = fields.Date(string="Start Date", required=False)
    end_date = fields.Date(string="End Date", required=False)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company, required=False)
    stage_id = fields.Many2one("agreement.stage",
                               string="Stage",
                               ondelete='restrict',  # Restrict the deletion of a record if a stage is related to it
                               copy=False,
                               index=True,
                               tracking=True,
                               default=_default_stage_id,
                               required=True,
                               group_expand='_read_group_expand_full'  # Always display all stages even if some of them have no records (!)
    )
    sequence = fields.Integer(default=10)
    key_obligations = fields.Text(string="Key Obligations")

    agreement_type = fields.Many2one('agreement.type', string="Agreement Type")
    legal_process_type = fields.Many2one('legal.process.type', string="Legal Process Type")
    renewal_terms = fields.Many2one("agreement.renewal.term", string="Renewal Terms")
    jurisdiction = fields.Many2one("agreement.jurisdiction", string="Jurisdiction")

    related_agreements = fields.Many2many(
        'pisa.agreement',
        'pisa_agreement_rel',
        'agreement_id',
        'related_agreement_id',
        string="Related Agreements",
        help="Agreements that are related to this one"
    )
    file_location = fields.Char(string="File Location (URL)")
    milestone_ids = fields.One2many('agreement.milestone', "agreement_id", string="Milestone")
