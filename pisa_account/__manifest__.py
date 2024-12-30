# -*- coding: utf-8 -*-
{
    'name': "PISA Accounting",

    'summary': "Customized features for PISA in the accounting application.",

    'description': """
        * Self-printed invoices
        * Invoice Approver Group: Permission to confirm invoices
    """,

    'author': "Penguin Infrastructure, José González",
    'website': "https://penguin.digital",

    'category': 'Accounting',
    'version': '18.0.1.0.0',
    'license': "OPL-1",

    'depends': ['base', 'l10n_py_selfprinted_invoice', 'secondary_currency'],

    'data': [
        'security/ir.model.access.csv',
        'security/account_security.xml',
        'views/account_journal_views.xml',
        'views/account_move_views.xml',
        'reports/invoice_report.xml',
        'wizards/edit_secondary_currency_rate_views.xml',
        'views/partner_view.xml',
    ],

    'demo': [
        'demo/account_journal_demo.xml',
    ],

    'i18n': ['i18n/es.po'],
}

