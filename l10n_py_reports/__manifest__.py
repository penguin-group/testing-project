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
    'depends': ['l10n_py'],
    'data': [
        'data/multicurrency_revaluation_report.xml',
        
        'wizard/multicurrency_revaluation.xml',
    ],
}
