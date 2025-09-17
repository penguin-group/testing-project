# -*- coding: utf-8 -*-
{
    'name': "Paraguay HR Reports",

    'summary': "", 

    'description': """
    """,

    'author': "Penguin Infrastructure",
    'maintainers': ['José González'],
    'website': "https://penguin.digital",
    'category': 'Project',
    'version': '18.0.1.0.0',
    'license': "OPL-1", 

    'depends': ['base', 'l10n_py_hr_payroll'],

    'data': [
        'security/ir.model.access.csv',
        'views/hr_reports_mtess_views.xml',
        'wizard/hr_reports_mtess_wizard_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'l10n_py_hr_reports/static/src/js/mtess_list_controller.js',
            'l10n_py_hr_reports/static/src/xml/mtess_list_buttons.xml',
        ],
    },
}
