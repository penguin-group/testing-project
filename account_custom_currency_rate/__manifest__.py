# -*- coding: utf-8 -*-
{
    'name': "Custom Currency Rate",

    'summary': "Custom Currency Rate",

    'description': """
    """,

    'author': "Penguin Infrastructure, David Paez",
    'website': "https://penguin.digital",
    'category': 'Accounting',
    'version': '18.0.1.0.0',
    'license': "OPL-1",

    'depends': ['base', 'account', 'web'],

    "data": [
        "security/ir.model.access.csv",
        "views/account_move_views.xml",
        "wizards/invoice_edit_currency_rate_views.xml",
    ],

    'i18n': ['i18n/es.po'],
}

