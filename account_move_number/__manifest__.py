# -*- coding: utf-8 -*-
{
    'name': "account_move_number",

    'summary': """
Se crea una numeración correlativa para los asientos contables
""",

    'description': """
Se crea una numeración correlativa para los asientos contables
    """,

    'author': "Interfaces S.A., Cristhian Cáceres",
    'website': "https://www.interfaces.com.,py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '17.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'data/data.xml',
    ],
}
