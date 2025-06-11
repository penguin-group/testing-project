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

    'depends': ['base', 'account_accountant', 'l10n_py', 'l10n_py_selfprinted_invoice', 'secondary_currency', 'account_custom_currency_rate'],

    'data': [
        'security/account_security.xml',
        'security/ir.model.access.csv',
        'views/account_journal_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'reports/invoice_report.xml',
        'wizards/edit_secondary_currency_rate_views.xml',
        'views/partner_view.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'pisa_account/static/src/components/bank_reconciliation/*',
        ],
    },
    'demo': [
        'demo/account_journal_demo.xml',
    ],

    'i18n': ['i18n/es.po'],
}

