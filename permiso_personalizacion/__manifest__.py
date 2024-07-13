# -*- coding: utf-8 -*-
{
    'name': "permiso_personalizacion",

    'summary': """
        permiso_personalizacion
        """,

    'description': """
        Creacion de permiso
    """,

    'author': "Interfaces S.A. - Edgar Gonzalez",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '2024.02.14.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'data/groups.xml',
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode

}
