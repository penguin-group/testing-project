from odoo import fields, models


class GithubPullRequest(models.Model):
    _name = 'github.pull.request'
    _description = 'GitHub Pull Request'

    name = fields.Char(string='Title', required=True)
    number = fields.Integer(string='Pull Request Number')
    task_id = fields.Many2one('project.task', string='Task', ondelete='cascade')
    url = fields.Char(string='Commit URL')
    state = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('merged', 'Merged')
    ], string='State', default='open', required=True)
