{
    'name': "Excepción para bloqueo de periodos PISA y PASA",

    'summary': """
        Excepción de bloqueo de fechas contabilidad""",

    'description': """
        Excepción de bloqueo de fechas contabilidad para las empresas de PISA y PASA para el periodo de 2022-2023
    """,

    'author': "Penguin Infrastructure, Giuliano Díaz, David Páez",
    "license": "LGPL-3",
    'website': "https://penguin.digital",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '18.0.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'account_accountant'],

    # always loaded
    'data': [],
    # only loaded in demonstration mode
    'demo': [],
}