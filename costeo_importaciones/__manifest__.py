# -*- coding: utf-8 -*-
{
    'name': "Costeo de importaciones",

    'summary': """
        Reporte de costeo de importaciones""",

    'description': """
        Reporte de costeo de importaciones
    """,

    'author': "Interfaces S.A.",
    "license": "LGPL-3",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '17.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','stock_landed_costs','moneda_secundaria','report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/wizard_reporte.xml',
        'views/purchase_order.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
