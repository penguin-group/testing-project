# -*- coding: utf-8 -*-
{
    'name': 'OAuth Only Login',
    'version': '18.0.1.0.0',
    'category': 'Authentication',
    'summary': 'Hide email/password login and show only OAuth provider login options',
    'description': """
OAuth Only Login
================

This module customizes the login interface to hide traditional email/password
login fields and only display OAuth provider login options.

Features:
- Hides email and password input fields
- Hides forgot password link
- Hides signup link
- Keeps OAuth provider buttons visible
- Maintains proper inheritance of Odoo's authentication system
    """,
    'author': 'Penguin Infrastructure S.A.',
    'maintainers': ['William Eckerleben'],
    'website': 'https://penguin.digital',
    'license': 'OPL-1',
    'depends': [
        'base',
        'web',
        'auth_oauth',
        'auth_signup',
    ],
    'data': [
        'views/login_templates.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
} 