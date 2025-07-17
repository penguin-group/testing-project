# -*- coding: utf-8 -*-
{
    'name': "PISA Human Resources",

    'summary': "PISA Human Resources",

    'description': """
        Module to handle specific HR processes adapted to Penguin Infrastructure's business logic.
    """,

    'author': "Penguin Infrastructure, David Paez",
    'website': "https://penguin.digital",
    'category': 'Human Resources',
    'version': '18.0.1.0.0',
    'license': "OPL-1",

    'depends': ['base', 'account', 'web', 'base_import'],

    "data": [
        "security/ir.model.access.csv",
        "wizards/parse_attendance_file.xml"
    ],

    'assets': {
        'web.assets_backend': [
            'pisa_hr/static/src/js/import_action_extension.js',
            'pisa_hr/static/src/xml/import_action_extension.xml',
        ],
    },

    'i18n': ['i18n/es.po'],
}

