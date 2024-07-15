# -*- coding: utf-8 -*-
{
    'name': "Presupuesto financiero USD",

    'summary': """
       Presupuesto financiero USD""",

    'description': """
        Presupuesto financiero USD
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '17.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','moneda_secundaria'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/budget.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
