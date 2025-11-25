from odoo import fields, models, api
from github import Auth, Github
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"
    
    github_token = fields.Char('User Github Token')
    github_username = fields.Char('GitHub Username', compute='_compute_github_username', store=False, readonly=True)

    @api.depends('github_token')
    def _compute_github_username(self):
        """Compute GitHub username from token."""
        for user in self:
            user.github_username = False
            if user.github_token:
                try:
                    auth = Auth.Token(user.github_token)
                    g = Github(auth=auth)
                    github_user = g.get_user()
                    user.github_username = github_user.login
                except Exception as e:
                    _logger.warning(f"Failed to get GitHub username for user {user.id}: {e}")
                    user.github_username = False