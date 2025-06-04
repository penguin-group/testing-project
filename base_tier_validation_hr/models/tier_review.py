from odoo import fields, models

class TierReview(models.Model):
    _inherit = 'tier.review'

    job_id = fields.Many2one(related='definition_id.job_id')
    department_id = fields.Many2one(related='definition_id.department_id')
    
    def _get_reviewers(self):
        """
        Extend this method to include the users related to the job_id
        """
        if self.job_id:
            if self.department_id:
                return self.job_id.employee_ids.filtered(lambda emp: emp.department_id == self.department_id).user_id
            return self.job_id.employee_ids.user_id
        return super(TierReview, self)._get_reviewers()
