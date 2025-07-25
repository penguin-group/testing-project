# -*- coding: utf-8 -*-
{
    'name': "Interfisa Localization",

    'summary': "Interfisa Localization",

    'description': """
    """,

    'author': "Penguin Infrastructure, David Paez",
    'website': "https://penguin.digital",
    'category': 'Payroll',
    'version': '18.0.1.0.0',
    'license': "OPL-1",

    'depends': ['base', 'account', 'web', 'hr_payroll', 'payroll_banks'],

    "data": [
        # "views/hr_payslip_views.xml",
        "security/ir.model.access.csv",
        "views/payroll_bank_interfisa_views.xml",
    ],

    'i18n': ['i18n/es.po'],
}

