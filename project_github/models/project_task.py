# -*- coding: utf-8 -*-
from odoo import fields, models, api
from github import Auth, Github
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = "project.task"

    BRANCH_PREFIXES = [
        'feat',
        'fix',
        'chore',
        'refactor',
        'hotfix',
        'release',
    ]

    task_code = fields.Char(string='Code', compute="_compute_task_code", store=True)
    is_development_task = fields.Boolean(
        related='project_id.is_development_project',
        string="Is Development Task",
        help="Indicates if this task is part of a development project.",
        readonly=True,
    )
    branch_ids = fields.One2many(
        'github.branch',
        'task_id',
        string='GitHub Branches',
        help="Branches associated with this task in GitHub."
    )
    branch_count = fields.Integer(
        compute='_compute_github_branch_count',
        string='GitHub Branch Count',
        help="Number of GitHub branches associated with this task."
    )
    commit_ids = fields.One2many(
        'github.commit',
        'task_id',
        string='Commits',
        help="Commits associated with this task in GitHub."
    )
    commit_count = fields.Integer(
        compute='_compute_commit_count',
        string='Commit Count',
        help="Number of commits associated with this task."
    )
    pull_request_ids = fields.One2many(
        'github.pull.request',
        'task_id',
        string='Pull Requests',
        help="Pull requests associated with this task in GitHub."
    )
    pull_request_count = fields.Integer(
        compute='_compute_pull_request_count',
        string='Pull Request Count',
        help="Number of pull requests associated with this task."
    )
    
    def _compute_task_code(self):
        for task in self:
            if task.project_id:
                project_initials = ''.join([word[0].upper() for word in task.project_id.name.split() if word])
                task.task_code = f"{project_initials}-{task.id}"
            else:
                task.task_code = f"{task.id}"
    
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record._compute_task_code()
        return records

    def write(self, vals):
        result = super().write(vals)
        if 'project_id' in vals:
            self._compute_task_code()
        return result

    def _compute_github_branch_count(self):
        """Compute the count of GitHub branches associated with this task."""
        for task in self:
            task.branch_count = len(task.branch_ids)

    def _compute_commit_count(self):
        """Compute the count of commits associated with this task."""
        for task in self:
            task.commit_count = len(task.commit_ids)

    def _compute_pull_request_count(self):
        """Compute the count of pull requests associated with this task."""
        for task in self:
            task.pull_request_count = len(task.pull_request_ids)
    
    def action_view_github_branches(self):
        """Open the GitHub branches associated with this task."""
        action = self.env.ref('project_github.github_branch_action').sudo().read()[0]
        action['domain'] = [('task_id', '=', self.id)]
        return action

    def action_view_commits(self):
        """Open the commits associated with this task."""
        action = self.env.ref('project_github.github_commit_action').sudo().read()[0]
        action['domain'] = [('task_id', '=', self.id)]
        return action

    def action_view_pull_requests(self):
        """Open the pull requests associated with this task."""
        action = self.env.ref('project_github.github_pull_request_action').sudo().read()[0]
        action['domain'] = [('task_id', '=', self.id)]
        return action
    
    def action_create_github_branch(self):
        if not self.is_development_task:
            return

        # Open the wizard to create a new branch
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'github.branch.create.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_task_id': self.id,
            },
        }

    def _get_commits_start_date(self, repo, branch_name):
        """Get the last commit date for this task."""
        try:
            last_synced_commit = self.env['github.commit'].search([
                ('task_id', '=', self.id),
            ], order='commit_date desc', limit=1)
            if last_synced_commit:
                return last_synced_commit.commit_date
            
            # There is no last synced commit, so we need to get all the commits from the first commit date
            base_branch_commit = repo.get_branch(repo.default_branch).commit
            branch_commit = repo.get_branch(branch_name).commit
            base_commit = repo.compare(base_branch_commit.sha, branch_commit.sha).merge_base_commit
            return base_commit.commit.committer.date.replace(tzinfo=None)
        except Exception as e:
            _logger.error("Error getting commits start date for task %s: %s", self.id, e)
            return datetime.now()

    
    def _sync_github_commits(self):
        """Sync commits with odoo database"""
        self.ensure_one()
    
        auth = Auth.Token(self.project_id.company_id.github_token)
        g = Github(auth=auth)
        repo = g.get_repo(self.project_id.repo.full_name)

        new_vals_list = []
        
        for branch in self.branch_ids:
            commits = repo.get_commits(sha=branch.name, since=self._get_commits_start_date(repo, branch.name))
            
            for commit in commits:
                naive_commit_date = commit.commit.author.date.replace(tzinfo=None)
                new_vals_list.append({
                    'name': commit.commit.message,
                    'sha': commit.sha,
                    'task_id': self.id,
                    'commit_date': naive_commit_date,
                    'author_name': commit.commit.author.name,
                    'author_email': commit.commit.author.email,
                    'url': commit.html_url,
                })
        # Create new commits in a single call
        if new_vals_list:
            self.env['github.commit'].create(new_vals_list)
            self.env.cr.commit()

    def _sync_github_pull_requests(self):
        """Sync pull requests with odoo database"""
        self.ensure_one()
    
        auth = Auth.Token(self.project_id.company_id.github_token)
        g = Github(auth=auth)
        repo = g.get_repo(self.project_id.repo.full_name)

        existing_pull_requests = {
            pr.number: pr
            for pr in self.env['github.pull.request'].search([('task_id', '=', self.id)])
        }
        
        new_vals_list = []
        
        # Iterate through GitHub branches
        for branch in self.branch_ids:
            pulls = repo.get_pulls(head=f"{repo.owner.login}:{branch.name}")

            for pull in pulls:
                if pull.number in existing_pull_requests:
                    existing_pr = existing_pull_requests[pull.number]
                    if existing_pr.state != pull.state or existing_pr.name != pull.title:
                        existing_pr.write({
                            'name': pull.title,
                            'state': pull.state,
                            'url': pull.html_url,
                        })
                else:
                    new_vals_list.append({
                        'name': pull.title,
                        'number': pull.number,
                        'task_id': self.id,
                        'url': pull.html_url,
                        'state': pull.state,
                    })

        # Create new pull requests in a single call
        if new_vals_list:
            self.env['github.pull.request'].create(new_vals_list)
            self.env.cr.commit()