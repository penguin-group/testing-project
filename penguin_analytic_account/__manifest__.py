# -*- coding: utf-8 -*-
{
    'name': "penguin_analytic_account",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
    En este modulo se agruparan todas las operaciones respecto a cuentas analiticas
    """,

    'author': "Penguin",
    "license": "LGPL-3",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '18.0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_asset','analytic'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/account_move_views.xml',
        'views/inhe_view_account_asset_tree.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

