# -*- coding: utf-8 -*-
{
    'name': "multi_currency_reporting",

    'summary': "This module adds functions so that reports have the ability to be in multi-currency.",

    'description': """
This module adds functions so that reports have the ability to be in multi-currency.
    """,

    'author': "Penguin Infrastructure",
    'website': "https://penguin.digital",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '17.0.1.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}

