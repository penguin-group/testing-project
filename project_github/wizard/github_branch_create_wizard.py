from odoo import api, fields, models, _
from github import Auth, Github, GithubException
from odoo.exceptions import UserError, RedirectWarning
import re


def sanitize_string(s):
    """Sanitizes string to be compliant with Git's naming rules."""
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s)
    s = s.strip('-/')
    return s

class GithubBranchCreateWizard(models.TransientModel):
    _name = 'github.branch.create.wizard'
    _description = 'Create a new branch from a task'

    def _handle_github_auth_error(self):
        """Helper method to raise RedirectWarning for GitHub authentication errors."""
        action = self.env.ref('base.action_res_users_my').read()[0]
        action['res_id'] = self.env.user.id
        raise RedirectWarning(
            _("GitHub authentication failed. Please check your GitHub token in your profile."),
            action,
            _('Edit My Profile')
        )

    def _get_default_source_branch(self):
        master_branch = self.env['github.branch'].search([('name', 'in', ['main', 'master'])], limit=1)        
        if master_branch:
            return master_branch.id
        return False
    
    task_id = fields.Many2one('project.task', string='Task', required=True, readonly=True)
    source_branch_id = fields.Many2one('github.branch', string='Create from branch', required=True, default=_get_default_source_branch)
    new_branch_name = fields.Char(string='New branch name', required=True)

    @api.onchange('task_id')
    def _onchange_task_id(self):
        """Set a default branch name based on the task code."""
        if self.task_id:
            self.task_id._compute_task_code()
            if self.task_id.tag_ids:
                branch_prefix = next((prefix for prefix in self.task_id.BRANCH_PREFIXES if self.task_id.tag_ids[0].name == prefix), 'feat')
            else:
                branch_prefix = 'feat'
            self.new_branch_name = f"{branch_prefix}/{self.task_id.task_code}-{sanitize_string(self.task_id.name)}"

    def action_create_branch(self):
        """Create the branch and close the wizard."""
        self.ensure_one()
        
        if not self.new_branch_name:
            raise UserError(_("The branch contains an invalid character."))
        if not self.env.user.github_token:
            action = self.env.ref('base.action_res_users_my').read()[0]
            action['res_id'] = self.env.user.id
            raise RedirectWarning(
                _("GitHub token is not configured for the current user."),
                action,
                _('Edit My Profile')
            )

        try:
            auth = Auth.Token(self.env.user.github_token)
            g = Github(auth=auth)
            repo = g.get_repo(self.task_id.project_id.repo.full_name)
            
            source_sha = self.source_branch_id.commit_sha
            
            repo.create_git_ref(
                ref=f"refs/heads/{self.new_branch_name}",
                sha=source_sha
            )
            
        except GithubException as e:
            if e.status == 401:
                self._handle_github_auth_error()
            elif e.status == 422:
                error_message = e.data.get('message', 'Invalid branch name')
                raise UserError(_("Failed to create branch: %s") % error_message)
            else:
                raise UserError(_("An unexpected GitHub error occurred: %s") % e)
        except Exception as e:
            raise UserError(_("An error occurred: %s") % e)

        # Create the Odoo record after successful branch creation
        self.env['github.branch'].create({
            'name': self.new_branch_name,
            'project_id': self.task_id.project_id.id,
            'task_id': self.task_id.id,
            'commit_sha': source_sha,
            'url': f"https://github.com/{self.task_id.project_id.repo.full_name}/tree/{self.new_branch_name}",
        })

        return {'type': 'ir.actions.act_window_close'}