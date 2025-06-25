# -*- coding: utf-8 -*-
{
    'name': "Completion Certificates",

    'summary': "Allows incremental vendor bills tied to purchase progress.",

    'description': """
        Allows incremental vendor bills tied to purchase progress, 
        ensuring transparent and structured billing throughout the service lifecycle.
    """,

    'author': "Penguin Infrastructure",
    'maintainers': ['José González'],
    'website': "https://penguin.digital",
    'category': 'Purchase',
    'version': '18.0.1.1.0',
    'license': "OPL-1", 

    'depends': ['base', 'purchase', 'account_accountant', 'portal', 'website'],

    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/certificate_views.xml',
        'views/purchase_order_views.xml',
        'views/portal_templates.xml',
        'views/portal_menu.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'completion_certificates/static/src/css/certificate_portal.css',
            'completion_certificates/static/src/certificate_portal_form/**/*',
        ],
    },
}

