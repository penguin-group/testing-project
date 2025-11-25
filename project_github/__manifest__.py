# -*- coding: utf-8 -*-
{
    'name': "Project GitHub Integration",

    'summary': "Project GitHub Integration",

    'description': """
        Project GitHub Integration
    """,

    'author': "Penguin Infrastructure S.A.",
    'mantainers': ['José González', 'William Eckerleben'],
    'website': "https://penguin.digital",

    'category': 'Project',
    'version': '18.0.1.0.0',
    'license': "OPL-1",

    'depends': ['base', 'project'],

    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/res_config_settings_views.xml',
        'views/res_users_views.xml',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'views/github_branch_views.xml',
        'views/github_commit_views.xml',
        'views/github_pull_request_views.xml',
        'wizard/github_branch_create_wizard_views.xml',
        'wizard/github_pr_create_wizard_views.xml'
    ],
}
