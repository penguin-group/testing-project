from odoo import fields, models, api
from odoo.exceptions import ValidationError


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

    @api.constrains('review_type', 'job_id', 'department_id')
    def _check_employee_exists(self):
        for record in self:
            if record.review_type == 'job':
                domain = [('job_id', '=', record.job_id.id)]
                if record.department_id:
                    domain.append(('department_id', '=', record.department_id.id))
                employee_count = self.env['hr.employee'].search_count(domain)
                if employee_count == 0:
                    raise ValidationError(
                        "No employee found for the selected role (and department)."
                    )

    @api.onchange("review_type")
    def onchange_review_type(self):
        """
        Extending the original method to add the job_id and department_id fields
        """
        super(TierDefinition, self).onchange_review_type()
        self.job_id = None
        self.department_id = None

    
