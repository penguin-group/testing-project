# -*- coding: utf-8 -*-
{
    'name': "Usar cotizacion de la importación en facturas de despacho",

    'summary': """
        Usar cotizacion de la importación en facturas de despacho al calcular moneda secundaria""",

    'description': """
        Usar cotizacion de la importación en facturas de despacho al calcular moneda secundaria
    """,

    'author': "Interfaces S.A.",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','interfaces_tipo_cambio_compra_venta','moneda_secundaria','purchase_stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
