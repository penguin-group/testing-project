from odoo import models, api, fields


class Agreement(models.Model):
    _name = 'agreement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Agreement'
    _order = 'sequence, id'

    def _default_stage_id(self):
        # Stages are ordered by sequence first.
        # In a kanban view, for example, the lower the sequence of the stage,
        # the further to the left it is going to be.
        stage = self.env['agreement.stage'].search([('active', '=', True)], order="sequence", limit=1).id
        return stage if stage else False

    name = fields.Char(string="Agreement Name", required=True, default="New Agreement", tracking=True)
    partner_ids = fields.Many2many('res.partner', string="Partner", required=False, tracking=True)
    signature_date = fields.Date(string="Signature Date", required=False, tracking=True)
    start_date = fields.Date(string="Start Date", required=False, tracking=True)
    end_date = fields.Date(string="End Date", required=False, tracking=True)
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
    key_obligations = fields.Text(string="Key Obligations", tracking=True)
    active = fields.Boolean(default=True)

    agreement_type = fields.Many2one('agreement.type', string="Agreement Type", tracking=True)
    legal_process_type = fields.Many2one('agreement.legal.process.type', string="Legal Process Type", tracking=True)
    renewal_terms = fields.Many2one("agreement.renewal.term", string="Renewal Terms", tracking=True)
    jurisdiction = fields.Many2one("agreement.jurisdiction", string="Jurisdiction", tracking=True)

    related_agreements = fields.Many2many(
        'agreement',
        'agreement_rel',
        'agreement_id',
        'related_agreement_id',
        string="Related Agreements",
        help="Agreements that are related to this one",
        tracking=True
    )
    file_location = fields.Char(string="File Location (URL)", tracking=True)
    milestone_ids = fields.One2many('agreement.milestone', "agreement_id", string="Milestone", tracking=True)
