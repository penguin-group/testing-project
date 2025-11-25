from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning
from github import Auth, Github, GithubException
from openai import OpenAI
import logging

_logger = logging.getLogger(__name__)


class GithubPRCreateWizard(models.TransientModel):
    _name = "github.pr.create.wizard"
    _description = "GitHub Pull Request Creation Wizard"

    task_id = fields.Many2one("project.task", required=True, readonly=True)

    def _handle_github_auth_error(self):
        """Helper method to raise RedirectWarning for GitHub authentication errors."""
        action = self.env.ref('base.action_res_users_my').read()[0]
        action['res_id'] = self.env.user.id
        raise RedirectWarning(
            _("GitHub authentication failed. Please check your GitHub token in your profile."),
            action,
            _('Edit My Profile')
        )
    
    def _get_head_branch_domain(self):
        if self.task_id:
            branch_ids = self.task_id.branch_ids.ids
            return [("id", "in", branch_ids)]
        return [("id", "=", False)]

    def _get_reviewer_domain(self):
        """Return domain for reviewers field: users with GitHub token, excluding current user."""
        return [
            ('github_token', '!=', False),
            ('id', '!=', self.env.user.id),
        ]

    base_branch_id = fields.Many2one("github.branch", string="Base Branch", required=True)
    head_branch_id = fields.Many2one(
        "github.branch",
        string="Head Branch",
        required=True,
        domain=_get_head_branch_domain,
    )
    title = fields.Char(string="PR Title")
    description = fields.Text(string="PR Description")
    reviewer_ids = fields.Many2many(
        "res.users",
        string="Reviewers",
        domain=_get_reviewer_domain,
        help="Select reviewers for this pull request. Only users with GitHub token configured are shown."
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        task = self.env["project.task"].browse(self.env.context.get("active_id"))

        if not task:
            raise UserError("No active task found in context.")

        # Default base = "qa" if exists, otherwise first available
        base_branch = self.env["github.branch"].search([
            ("project_id", "=", task.project_id.id),
            ("name", "=", "qa")
        ], limit=1)
        if not base_branch:
            base_branch = self.env["github.branch"].search([("project_id", "=", task.project_id.id)], limit=1)

        head_branch = task.branch_ids[:1]

        res.update({
            "task_id": task.id,
            "base_branch_id": base_branch.id if base_branch else False,
            "head_branch_id": head_branch.id if head_branch else False,
        })
        return res

    def action_generate_title_description(self):
        """Generate PR title and description using OpenAI based on the diff."""
        self.ensure_one()

        if not self.env.user.github_token:
            action = self.env.ref('base.action_res_users_my').read()[0]
            action['res_id'] = self.env.user.id
            raise RedirectWarning(
                _("GitHub token is not configured for the current user."),
                action,
                _('Edit My Profile')
            )

        try:
            project = self.task_id.project_id
            auth = Auth.Token(self.env.user.github_token)
            g = Github(auth=auth)
            repo = g.get_repo(self.task_id.project_id.repo.full_name)

            if not repo:
                raise UserError("No repository is linked to this project.")
            if not project.openai_api_key:
                raise UserError("OpenAI API key is not configured in the project.")

            # Get diff using local repo object
            comparison = repo.compare(self.base_branch_id.name, self.head_branch_id.name)
            diff_text = ""
            for file in comparison.files:
                diff_text += f"### {file.filename}\n```diff\n{file.patch}\n```\n"
            if not diff_text:
                raise UserError("No differences found between the selected branches.")

            # Generate AI prompt
            prompt = project.openai_prompt_template % diff_text

            client = OpenAI(api_key=project.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful GitHub assistant. Respond with exactly: first line = title, remaining lines = description."
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )

            generated = response.choices[0].message.content or ""
            lines = generated.strip().split('\n')
            
            if not lines or len(lines) < 2:
                raise UserError(_("Invalid AI response format. Expected title and description but got:\n%s") % generated)
                
            title = f"[{self.task_id.task_code}] {lines[0].strip()}"
            description = '\n'.join(lines[1:]).strip()
            
            self.title = title
            self.description = description

            return {
                "type": "ir.actions.act_window",
                "res_model": "github.pr.create.wizard",
                "view_mode": "form",
                "res_id": self.id,
                "target": "new",
            }
        
        except GithubException as e:
            if e.status == 401:
                self._handle_github_auth_error()
            raise UserError(self._format_github_error(e))
        except Exception as e:
            raise UserError(_("An error occurred: %s") % e)

    def action_create_pull_request(self):
        """Create the PR on GitHub."""
        self.ensure_one()
        if not self.title or not self.description:
            raise UserError(_("PR title and description must be provided."))
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

            pr = repo.create_pull(
                title=self.title,
                body=self.description,
                base=self.base_branch_id.name,
                head=self.head_branch_id.name,
            )

            # Assign the PR creator as assignee
            try:
                current_user = g.get_user()
                pr.add_to_assignees(current_user.login)
            except Exception as e:
                # If assigning fails, log but don't fail the PR creation
                _logger.warning(f"Failed to assign PR creator as assignee: {e}")

            # Request reviewers
            if self.reviewer_ids:
                try:
                    reviewers = []
                    for reviewer in self.reviewer_ids:
                        if reviewer.github_username:
                            reviewers.append(reviewer.github_username)
                        else:
                            # Try to get username from token if not computed
                            try:
                                auth = Auth.Token(reviewer.github_token)
                                g_reviewer = Github(auth=auth)
                                github_user = g_reviewer.get_user()
                                reviewers.append(github_user.login)
                            except Exception as e:
                                _logger.warning(f"Failed to get GitHub username for reviewer {reviewer.name}: {e}")
                    
                    if reviewers:
                        pr.create_review_request(reviewers=reviewers)
                except Exception as e:
                    # If requesting reviewers fails, log but don't fail the PR creation
                    _logger.warning(f"Failed to request reviewers: {e}")

            # Link the PR to the task
            self.env['github.pull.request'].create({
                'name': pr.title,
                'number': pr.number,
                'task_id': self.task_id.id,
                'url': pr.html_url,
                'state': pr.state,
            })

            return self.task_id.action_view_pull_requests()
        
        except GithubException as e:
            if e.status == 401:
                self._handle_github_auth_error()
            raise UserError(self._format_github_error(e))
        except Exception as e:
            raise UserError(_("An error occurred: %s") % e)

    def _format_github_error(self, exc):
        """Return a user friendly message for common GitHub API error payloads."""
        try:
            data = getattr(exc, "data", None)
            # Typical PyGithub payload: {'message': 'Validation Failed', 'errors': [{...}], ...}
            if isinstance(data, dict):
                errors = data.get("errors") or []
                msgs = []
                for er in errors:
                    resource = er.get("resource")
                    field = er.get("field")
                    code = er.get("code")
                    if resource == "PullRequest" and field in ["head", "base"] and code == "invalid":
                        branch = getattr(self, f"{field}_branch_id", None) 
                        msgs.append(
                            _(
                                "The head branch '%s' is not a valid remote branch on GitHub. "
                                "Make sure the branch exists in the repository and has been pushed to GitHub."
                            ) % branch.name or _("the selected branch")
                        )
                    else:
                        # try to format known pieces, fallback to the whole error dict
                        piece = ", ".join(f"{k}={v}" for k, v in er.items() if v)
                        msgs.append(piece or str(er))
                if msgs:
                    return _("GitHub error: %s") % ("; ".join(msgs))

                # if no errors list but message present
                if data.get("message"):
                    return _("GitHub error: %s") % data.get("message")
        except Exception:
            # fall through to generic message on unexpected formats
            pass

        # Fallback: include original exception string
        return _("An unexpected GitHub error occurred: %s") % str(exc)

