from odoo import models, fields, api, _
from odoo.exceptions import UserError
from github import Auth, Github, GithubException
from openai import OpenAI


class GithubPRCreateWizard(models.TransientModel):
    _name = "github.pr.create.wizard"
    _description = "GitHub Pull Request Creation Wizard"

    task_id = fields.Many2one("project.task", required=True, readonly=True)
    
    def _get_head_branch_domain(self):
        if self.task_id:
            branch_ids = self.task_id.branch_ids.ids
            return [("id", "in", branch_ids)]
        return [("id", "=", False)]

    base_branch_id = fields.Many2one("github.branch", string="Base Branch", required=True)
    head_branch_id = fields.Many2one(
        "github.branch",
        string="Head Branch",
        required=True,
        domain=_get_head_branch_domain,
    )
    title = fields.Char(string="PR Title")
    description = fields.Text(string="PR Description")

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

        try:
            project = self.task_id.project_id
            auth = Auth.Token(self.task_id.project_id.company_id.github_token)
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

            # Generate AI prompt
            prompt = (
                "You are a GitHub assistant. "
                "Based on the following git diff, generate a concise pull request title and description. "
                "Return plain text only — no labels, prefixes, or markdown formatting.\n\n"
                f"Diff:\n{diff_text}"
            )

            client = OpenAI(api_key=project.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful GitHub assistant."},
                    {"role": "user", "content": prompt},
                ],
            )

            generated = response.choices[0].message.content or ""
            lines = generated.split("\n", 1)
            title = f"[{self.task_id.task_code}] {lines[0].strip().replace("Title: ", "")}"
            description = lines[1].strip().replace("Description: ", "") if len(lines) > 1 else ""

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
            raise UserError(_("An unexpected GitHub error occurred: %s") % e)
        except Exception as e:
            raise UserError(_("An error occurred: %s") % e)

    def action_create_pull_request(self):
        """Create the PR on GitHub."""
        self.ensure_one()
        
        try:
            auth = Auth.Token(self.task_id.project_id.company_id.github_token)
            g = Github(auth=auth)
            repo = g.get_repo(self.task_id.project_id.repo.full_name)

            pr = repo.create_pull(
                title=self.title,
                body=self.description,
                base=self.base_branch_id.name,
                head=self.head_branch_id.name,
            )

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
            raise UserError(_("An unexpected GitHub error occurred: %s") % e)
        except Exception as e:
            raise UserError(_("An error occurred: %s") % e)
