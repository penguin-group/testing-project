from odoo import models, fields
from github import Auth, Github


class GithubBranch(models.Model):
    _name = 'github.branch'
    _description = 'GitHub Branch'
    _rec_name = 'name'

    name = fields.Char('Branch Name', required=True)
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        ondelete='cascade',
        help="The project this branch belongs to."
    )
    task_id = fields.Many2one('project.task', string='Task associated with this branch', ondelete='cascade')
    commit_sha = fields.Char('Commit SHA', help="The SHA of the latest commit on this branch.")
    url = fields.Char(string='URL')
    last_updated = fields.Datetime('Last Updated', help="The last time this branch was updated.")

    
    