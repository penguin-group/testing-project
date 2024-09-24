# -*- coding: utf-8 -*-
{
    'name': "PISA Accounting",

    'summary': "Customized features for PISA in the accounting application.",

    'description': """
        * Self-printed invoices
    """,

    'author': "Penguin Infrastructure, José González",
    'website': "https://penguin.digital",

    'category': 'Accounting',
    'version': '17.0.1.1.1',

    'depends': ['base', 'l10n_py'],

    'data': [
        'views/account_journal_views.xml',
        'views/account_move_views.xml',
        'reports/invoice_report.xml',
    ]
}

