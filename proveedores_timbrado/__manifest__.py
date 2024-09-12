# -*- coding: utf-8 -*-
{
    'name': "Timbrado de proveedores",

    'summary': """
        Modulo que contiene el timbrado del proveedor""",

    'description': """
       Timbrado para los proveedores
    """,

    'author': "Interfaces S.A., Edgar Páez, Cristhian Cáceres",
    "license": "LGPL-3",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'interfaces_timbrado'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/account_move.xml',
        'views/timbrado.xml',
        'views/res_partner.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
