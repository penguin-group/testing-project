from odoo import models, fields, api
from github import Auth, Github
import logging
from datetime import timezone
import re

_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = "project.project"

    is_development_project = fields.Boolean(
        string="Is Development Project",
        help="Check this box if the project is a development project.",
    )

    @api.onchange('is_development_project', 'company_id')
    def _onchange_development_project(self):
        """Update available repositories"""
        if self.is_development_project and self.company_id and self.company_id.github_token:
            self._sync_github_repos()
        
        # Set domain for repo field
        domain = [('company_id', '=', self.company_id.id if self.company_id else False)]
        if not self.is_development_project:
            domain = [('id', '=', False)]  # No repos available
            
        return {'domain': {'repo': domain}}
    
    def _sync_github_repos(self):
        """Sync GitHub repositories for current company"""
        if not (self.company_id and self.company_id.github_token):
            return
            
        try:
            auth = Auth.Token(self.company_id.github_token)
            g = Github(auth=auth)
            user = g.get_user()
            org = g.get_organization(self.company_id.github_organization) if self.company_id.github_organization else None
            repos = org.get_repos() if org else user.get_repos()
            
            # Clear existing repos for this company
            existing_repos = self.env['github.repository'].search([
                ('company_id', '=', self.company_id.id)
            ])
            existing_repos.unlink()
            
            # Create new repos
            for repo in repos:
                self.env['github.repository'].create({
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'company_id': self.company_id.id,
                })
                
        except Exception as e:
            _logger.error(f"Error syncing GitHub repos: {e}")
    
    repo = fields.Many2one(
        'github.repository',
        string='Repository',
        domain="[('company_id', '=', company_id)]"
    )

    def _sync_github_branches(self):
        """Sync branches with odoo database"""
        self.ensure_one()
    
        auth = Auth.Token(self.company_id.github_token)
        g = Github(auth=auth)
        repo = g.get_repo(self.repo.full_name)
        
        # Fetch all existing branches for this project and map them by name
        existing_branches = {
            branch.name: branch
            for branch in self.env['github.branch'].search([('project_id', '=', self.id)])
        }

        new_vals_list = []
        to_delete_branch_ids = set(existing_branches.keys())
        
        # 1. Fetch all tasks for the current project in a single query
        all_project_tasks = self.env['project.task'].search([('project_id', '=', self.id)])
        
        # 2. Build the task mapping in memory using the computed field
        task_mapping = {
            task.task_code: task.id 
            for task in all_project_tasks
        }
        
        # Iterate through GitHub branches
        for branch in repo.get_branches():
            task_code = self._extract_task_code_from_branch_name(branch.name)
            task_id = task_mapping.get(task_code, False)
            
            if branch.name in existing_branches:
                # Update existing branch
                existing_branch = existing_branches[branch.name]
                if existing_branch.commit_sha != branch.commit.sha or existing_branch.task_id.id != task_id:
                    existing_branch.write({
                        'commit_sha': branch.commit.sha,
                        'task_id': task_id,
                        'url': f"https://github.com/{self.repo.full_name}/tree/{branch.name}",
                    })
                to_delete_branch_ids.discard(branch.name)
            else:
                # Create a new branch record
                new_vals_list.append({
                    'name': branch.name,
                    'commit_sha': branch.commit.sha,
                    'project_id': self.id,
                    'task_id': task_id,
                    'url': f"https://github.com/{self.repo.full_name}/tree/{branch.name}",
                })
                
        # Create new branches
        if new_vals_list:
            self.env['github.branch'].create(new_vals_list)
            
        # Delete stale branches
        if to_delete_branch_ids:
            self.env['github.branch'].search([
                ('project_id', '=', self.id),
                ('name', 'in', list(to_delete_branch_ids))
            ]).unlink()

    def _extract_task_code_from_branch_name(self, branch_name):
        """
        Extract task code from branch name format: type/task_code-task-description
        Example: feat/OI-75-The-test-task -> OI-75
        """
        # Pattern to match: type/TASK_CODE-description
        # Assumes task code format: LETTERS-NUMBERS (like OI-75, PROJ-123, etc.)
        pattern = r'^[^/]+/([A-Z]+-\d+)-.*'
        
        match = re.match(pattern, branch_name)
        if match:
            return match.group(1)
        return None

    @api.model
    def _cron_sync_all_github_data(self):
        """Cron job to sync branches for all projects with GitHub integration"""
        projects = self.search([
            ('repo', '!=', False),
            ('is_development_project', '!=', False)
        ])
        
        for project in projects:
            try:
                project._sync_github_branches()
                for task in project.task_ids:
                    task._sync_github_commits()
                    task._sync_github_pull_requests()
                _logger.info("Successfully synced branches for project: %s", project.name)
                self.env.cr.commit()  # Commit after each project to avoid losing progress
            except Exception as e:
                _logger.error("Failed to sync branches for project %s: %s", project.name, str(e))
                self.env.cr.rollback()
                continue