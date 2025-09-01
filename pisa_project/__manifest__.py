# -*- coding: utf-8 -*-
{
    'name': "PISA Project",

    'summary': "Custom enhancements for project management in Odoo, tailored for PISA requirements.",

    'description': """
This module extends Odoo's Project application to support custom workflows and permissions for PISA projects. 
It introduces a new 'Manager' group with specific access rights and record rules, allowing team managers to 
fully manage their own projects and related records (such as stages, tasks, tags, milestones, collaborators, 
and analytic accounts). 
Project managers can only view and manage the projects they have created, ensuring data privacy and responsibility. 
    """,

    'author': "Penguin Infrastructure",
    'maintainers': ['José González'],
    'website': "https://penguin.digital",
    'category': 'Project',
    'version': '18.0.1.0.0',
    'license': "OPL-1", 

    'depends': ['base', 'project', 'hr'],

    'data': [
        'security/project_security.xml',
        'security/ir.model.access.csv',
        'views/project_menus.xml',
        'views/project_task_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'pisa_project/static/src/js/*.js',
        ],
    },
}

