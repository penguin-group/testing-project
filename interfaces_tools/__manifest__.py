# -*- coding: utf-8 -*-
{
    'name': "Interfaces tools",

    'summary': """
        Módulo de herramientas estándares""",

    'description': """
        Módulo de herramientas estándares
    """,

    'author': "Interfaces S.A., Edgar Páez, Cristhian Cáceres",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '17.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'data/data.xml',
        'views/ir_module_module.xml',
    ],
}
