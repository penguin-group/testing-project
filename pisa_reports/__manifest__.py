# -*- coding: utf-8 -*-
{
    'name': "PISA Reports",

    'summary': "Customized reports for PISA",

    'description': """
        * Customized reports for PISA
    """,

    'author': "Penguin Infrastructure, José González",
    'website': "https://penguin.digital",

    'category': 'Accounting',
    'version': '18.0.1.0.0',
    'license': "OPL-1",

    'depends': ['base', 'account_reports', 'secondary_currency'],

    'data': [
        'data/pdf_export_templates.xml',
    ],

    'assets': {
        'account_reports.assets_pdf_export': [
            'pisa_reports/static/src/scss/pdf/pdf_pisa_report.scss',
        ],
    },


    
}