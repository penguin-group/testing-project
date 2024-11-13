# -*- coding: utf-8 -*-
{
    'name': "Secondary Currency",

    'summary': "Manages dual currencies for accurate transaction recording and reporting.",

    'description': """
        This module handles secondary currency so that transactions can be accurately recorded and reported 
        in dual currencies, facilitating international transactions and financial reporting.
    """,

    'author': "Penguin Infrastructure, José González",
    'website': "https://www.pengin.digital",

    'category': 'Accounting',
    'version': '17.0.0.1',

    'depends': ['base', 'account'],

    'data': [
        'views/res_company_views.xml',
        'views/account_move_views.xml',
    ],
    'demo': [
    ],
}

