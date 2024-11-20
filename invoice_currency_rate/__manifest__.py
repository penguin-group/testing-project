# -*- coding: utf-8 -*-
{
    'name': "Invoice Currency Rate",

    'summary': "This module allows to set currency rate for invoices",

    'description': """
        This module allows to set currency rate for invoices
    """,

    'author': "Penguin Infrastructure S.A., José González",
    'website': "https://penguin.digital",

    'category': 'Accounting',
    'version': '17.0.0.1',
    'license': "OPL-1",

    'depends': ['base', 'account'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move_views.xml',
    ],

}

