# -*- coding: utf-8 -*-
{
    'name': "Interfaces Timbrado",

    'summary': """
        Módulo de timbrado - Interfaces S.A.
        """,

    'description': """
        Módulo de timbrado - Interfaces S.A.
    """,

    'author': "Interfaces S.A.",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Invoicing',
    'version': '17.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'standard_ruc'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/timbrado.xml',
        'views/account_journal.xml',
        'views/account_move.xml',
    ],
}
