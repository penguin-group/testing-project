# -*- coding: utf-8 -*-
{
    'name': "PISA HR Reports",

    'summary': "PISA HR Reports",

    'description': """
        Module to generate HR reports adapted to Penguin Infrastructure's business logic.
    """,

    'author': "Penguin Infrastructure",
    'maintainers': ['José E. González'],
    'website': "https://penguin.digital",
    'category': 'Human Resources',
    'version': '1.0.0',
    'license': "OPL-1",

    'depends': ['base', 'l10n_py_hr_payroll'],

    "data": [
        "views/hr_payroll_report.xml",
        "views/report_payslip_templates.xml",
    ],

    'i18n': ['i18n/es.po'],
}

