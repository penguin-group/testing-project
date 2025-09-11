from odoo import fields, models


class GithubCommit(models.Model):
    _name = 'github.commit'
    _description = 'GitHub Commit'

    name = fields.Char(string='Commit Message', required=True)
    sha = fields.Char(string='SHA', required=True, index=True)
    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    commit_date = fields.Datetime(string='Commit Date')
    author_name = fields.Char(string='Author')
    author_email = fields.Char(string='Author Email')
    url = fields.Char(string='Commit URL')
