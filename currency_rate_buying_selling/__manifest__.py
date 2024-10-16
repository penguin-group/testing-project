# -*- coding: utf-8 -*-
{
    'name': "Management of buying/selling exchange rates",

    'summary': "Manage buying and selling exchange rates and apply appropriate FX rates based on the invoice type.",

    'author': "Penguin Infrastructure S.A., José González",
    'website': "https://penguin.digital",

    'category': 'Base',
    'version': '17.0.1.1.1',

    'depends': ['base', 'account'],

    'data': [
        'views/res_currency_views.xml',
        'views/account_move_views.xml',
    ],
}

