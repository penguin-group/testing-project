# -*- coding: utf-8 -*-
{
    'name': "PISA Payroll Banks",

    'summary': "PISA Payroll Banks",

    'description': """Module responsible for including settings related to banks used for payroll operations.
    """,

    'author': "Penguin Infrastructure",
    'maintainers': ['David Páez'],
    'website': "https://penguin.digital",
    'version': '18.0.1.0.0',
    'license': "OPL-1",

    'depends': ['base', 'account', 'web', 'hr_payroll'],

    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings.xml",
    ],

    'i18n': ['i18n/es.po'],
}

