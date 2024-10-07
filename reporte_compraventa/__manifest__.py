# -*- coding: utf-8 -*-
{
    'name': "Libros IVA Venta/Compra",

    'summary': """
        Libros IVA Venta/Compra""",

    'description': """
        Libros IVA Venta/Compra.

        Solo se cambian las posiciones de las columnas en el excel.
    """,

    'author': "Interfaces S.A., Edgar Páez, Cristhian Cáceres",
    "license": "LGPL-3",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Account',
    'version': '17.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'interfaces_timbrado', 'report_xlsx', 'cotizacion_asientos_moneda_secundaria'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
}
