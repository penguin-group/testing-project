from odoo import models, fields


class GithubRepository(models.Model):
    _name = 'github.repository'
    _description = 'GitHub Repository'
    _rec_name = 'full_name'

    name = fields.Char('Repository Name', required=True)
    full_name = fields.Char('Full Name', required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True)
    organization = fields.Char('Organization')
    project_id = fields.Many2one('project.project', 'Project')  # if you want to link to project
