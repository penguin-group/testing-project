# -*- coding: utf-8 -*-
{
    'name': "Ganancias/pérdidas de moneda secundaria sin realizar",

    'summary': """
        Ganancias/pérdidas de moneda secundaria sin realizar""",

    'description': """
        Ganancias/pérdidas de moneda secundaria sin realizar
    """,

    'author': "Interfaces S.A.",
    "license": "LGPL-3",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '17.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','moneda_secundaria','account_reports'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/adjustment.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
