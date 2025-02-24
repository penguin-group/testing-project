# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Accounting Reports',
    'summary': 'View and create reports',
    'category': 'Accounting/Accounting',
    'description': """
Accounting Reports
==================
    """,
    'depends': ['secondary_currency'],
    'data': [
        'data/multicurrency_revaluation_report.xml',
        
        'wizard/multicurrency_revaluation.xml',
    ],
    'version': '18.0.0.1',
    'assets': {
        'web.assets_backend': [
            'secondary_currency/static/src/components/**/*',
        ],
    },
}
