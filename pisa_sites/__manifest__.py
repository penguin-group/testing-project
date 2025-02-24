{
    'name': "PISA Sites",
    'summary': "Manage electrical sites and related information",
    'description': """
        Site Management System
        =====================
        
        This module allows you to:
        * Track sites and their details
        * Manage site states and tags
        * Monitor capacity and voltage levels
        * Track project progress
    """,
    'category': 'Industries',
    'version': '18.0.1.0.0',
    'depends': ['base', 'mail'],
    'data': [
        'security/site_security.xml',
        'security/ir.model.access.csv',
        'views/site_views.xml',
        'views/site_menus.xml',
    ],
    'application': True,
    'icon': '/pisa_sites/static/description/icon.png',
    'sequence': 1,
    'license': 'LGPL-3',
} 