# -*- coding: utf-8 -*-
{
    'name': "Paraguayan HR Reports",

    'summary': "Generates official HR reports required by Paraguayan Authorities.", 

    'description': """
        This module provides wizard-based generation of three mandatory Paraguayan labor reports: 
            Employee and Workers Report (Planilla de Empleados y Obreros), 
            Salaries and Wages Report (Planilla de Sueldos y Jornales), 
            and General Summary of Occupied Personnel (Resumen General de Personal Ocupado). 
        Features include year selection, XLSX export with proper formatting, 
        and integration under Payroll > Reporting menu with grouped list views for better organization.
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
        'views/hr_reports_ips_views.xml',
        'wizard/hr_reports_mtess_wizard_views.xml',
        'wizard/hr_reports_mtess_ips_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'l10n_py_hr_reports/static/src/js/mtess_list_controller.js',
            'l10n_py_hr_reports/static/src/xml/mtess_list_buttons.xml',
        ],
    },
}
