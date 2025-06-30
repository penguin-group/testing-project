# -*- coding: utf-8 -*-
{
    'name': 'PISA Dark Mode Default',
    'version': '18.0.1.0.0',
    'category': 'Hidden',
    'summary': 'Set dark mode as default theme for all users',
    'description': """
Set Dark Mode as Default Theme
===============================

This module automatically sets dark mode as the default theme for all users.
It implements the user story requirements:
- Dark mode becomes the default UI theme on initial access
- English remains the primary language
- Users retain the ability to manually switch to light mode or Spanish if desired
- Preferences persist across sessions for logged-in users

Features:
- Automatically sets dark mode cookie for new sessions
- Respects user preferences if already set
- Compatible with existing Odoo dark mode implementation
    """,
    'author': 'Penguin Infrastructure SA',
    'maintainers': ['William Eckerleben'],
    'website': 'https://www.penguin.digital',
    'depends': ['base', 'web'],
    'data': [
        'views/webclient_templates.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
    'license': 'OPL-1',
} 