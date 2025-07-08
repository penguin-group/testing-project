from odoo import models, fields, api, _


def get_all_descendants(department, list_of_ids):
    """Helper function to recursively get the children of each department."""
    list_of_ids.append(department.id)
    if len(department.child_ids) > 0:
        for child in department.child_ids:
            get_all_descendants(child, list_of_ids)


class HrDepartment(models.Model):
    _inherit = "hr.department"

    department_descendant_ids = fields.One2many('hr.department',
                                                'parent_id',
                                                compute="_compute_descendant_departments",
                                                string='All Descendant Departments')

    @api.depends('child_ids')
    def _compute_descendant_departments(self):
        """With 'self' being the root department, this compute method retrieves the IDs of all of self's descendants
        and then assigns them to department_descendant_ids."""
        descendant_ids = []
        get_all_descendants(self, descendant_ids)
        self.department_descendant_ids = [(6, 0, descendant_ids)]
