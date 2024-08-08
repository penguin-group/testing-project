# -*- coding: utf-8 -*-
{
    'name': "RRHH Novedades",

    'summary': """
       RRHH Novedades""",

    'description': """
        Módulo para el registro de novedades en las nóminas
    """,

    'author': "Interfaces S.A., Edgar Páez, Cristhian Cáceres",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources/Payroll',
    'version': '17.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'report_xlsx', 'hr_payroll', 'reportes_ministerio_trabajo_py', 'account_payment'],

    # always loaded
    'data': [
        'security/security.xml',
        'data/data.xml',
        'data/estructura_aguinaldo.xml',
        'security/ir.model.access.csv',
        'views/novedades.xml',
        'views/novedades_batch.xml',
        'views/hr_payslip.xml',
    ],
}
