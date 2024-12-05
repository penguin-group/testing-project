# -*- coding: utf-8 -*-
{
    'name': "PISA Account Fix",

    'summary': "PISA Account Fix",

    'description': """
        * Fixes journal entries' credit and debit amounts in assets depreciation.
    """,

    'author': "Penguin Infrastructure, José González",
    'website': "https://penguin.digital",

    'category': 'Accounting',
    'version': '17.0.1.0',

    'depends': ['base', 'account_asset'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/account_asset_views.xml',
        'views/account_move_views.xml',
    ],
}

