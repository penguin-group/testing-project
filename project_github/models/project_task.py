# -*- coding: utf-8 -*-
from odoo import fields, models, api
from github import Auth, Github, GithubException
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
        action = self.env.ref('project_github.github_branch_action').read()[0]
        action['domain'] = [('task_id', '=', self.id)]
        return action

    def action_view_commits(self):
        """Open the commits associated with this task."""
        action = self.env.ref('project_github.github_commit_action').read()[0]
        action['domain'] = [('task_id', '=', self.id)]
        return action

    def action_view_pull_requests(self):
        """Open the pull requests associated with this task."""
        action = self.env.ref('project_github.github_pull_request_action').read()[0]
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

    def _get_commits(self, repo, branch_name):
        """Get all commits in the branch and filter by message content."""
        commits = repo.get_commits(sha=branch_name)
        return [commit for commit in commits if self.task_code in commit.commit.message]

    
    def _sync_github_commits(self):
        """Sync commits with odoo database."""
        self.ensure_one()

        # Authenticate with GitHub
        auth = Auth.Token(self.project_id.company_id.github_token)
        g = Github(auth=auth)
        repo = g.get_repo(self.project_id.repo.full_name)

        repo.get_commits()

        new_vals_list = []
        
        for branch in self.branch_ids:
            # Step 1: Find the SHA of the last commit synced for this branch
            last_commit = self.env['github.commit'].search([
                ('task_id', '=', self.id),
            ], order='commit_date desc', limit=1)

            commits_to_process = []
            try:
                if not last_commit:
                    commits_to_process = self._get_commits(repo, branch.name)
                else:
                    comparison = repo.compare(base=last_commit.sha, head=branch.name)
                    commits_to_process = comparison.commits
            except GithubException as e:
                # Handle cases where the base commit was part of a force-push or rebase
                # and no longer exists in the branch's history.
                _logger.warning(
                    "Could not compare commits for branch %s starting from %s. "
                    "Refetching all commits. Error: %s",
                    branch.name, last_commit.sha, e
                )
                commits_to_process = self._get_commits(repo, branch.name)

            for commit in commits_to_process:
                # The commit date from PyGithub is timezone-aware.
                # Odoo's Datetime fields expect naive UTC datetime objects.
                naive_utc_date = commit.commit.author.date.replace(tzinfo=None)
                
                new_vals_list.append({
                    'name': commit.commit.message,
                    'sha': commit.sha,
                    'task_id': self.id,
                    'commit_date': naive_utc_date, # Use the naive datetime
                    'author_name': commit.commit.author.name,
                    'author_email': commit.commit.author.email,
                    'url': commit.html_url,
                })

        # Create all new commits in a single database call for efficiency
        if new_vals_list:
            # To avoid creating duplicates if a full refetch happens,
            # check for existing SHAs before creating.
            existing_shas = self.env['github.commit'].search_read(
                [('sha', 'in', [vals['sha'] for vals in new_vals_list])],
                ['sha']
            )
            existing_shas_set = {rec['sha'] for rec in existing_shas}
            
            final_vals_list = [
                vals for vals in new_vals_list if vals['sha'] not in existing_shas_set
            ]

            if final_vals_list:
                self.env['github.commit'].create(final_vals_list)
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