# -*- coding: utf-8 -*-
from odoo import fields,models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_code = fields.Char(string='Code', compute="_compute_task_code", store=True)

    def _compute_task_code(self):
        for task in self:
            if task.project_id:
                project_initials = ''.join([word[0].upper() for word in task.project_id.name.split() if word])
                task.task_code = f"{project_initials}-{task.id}"
            else:
                task.task_code = f"{task.id}"