from odoo import fields, models, api


class TierDefinition(models.Model):
    _inherit = 'tier.definition'

    review_type = fields.Selection(
        selection_add=[('job', 'Job Position')]
    )
    job_id = fields.Many2one(
        'hr.job',
        string='Job Position'
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department'
    )

    @api.onchange("review_type")
    def onchange_review_type(self):
        """
        Extending the original method to add the job_id and department_id fields
        """
        super(TierDefinition, self).onchange_review_type()
        self.job_id = None
        self.department_id = None

    
