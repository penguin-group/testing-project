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

    'depends': ['base', 'account', 'web'],

    "data": [
        "security/ir.model.access.csv",
        "views/hr_attendance_views.xml",
        "wizards/import_attendance_records.xml"
    ],

    'i18n': ['i18n/es.po'],
}

