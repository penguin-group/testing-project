# -*- coding: utf-8 -*-
{
    'name': "Secondary Currency Migration",

    'summary': "Secondary Currency Data Migration",

    'description': """
        Secondary Currency Data Migration
    """,

    'author': "Penguin Infrastructure S.A., José González",
    'website': "https://penguin.digital",

    'category': 'Accounting',
    'version': '17.0.0.1',

    'depends': ['base', 'account', 'secondary_currency', 'moneda_secundaria'],

    'data': [
        # 'security/ir.model.access.csv',
        'data/ir_cron.xml',
        'views/account_move_views.xml',
    ],

}

