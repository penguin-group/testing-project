# -*- coding: utf-8 -*-
{
    'name': "PISA HR",

    'summary': "PISA Human Resources",

    'description': """
        Module to handle specific HR processes adapted to Penguin Infrastructure's business logic.
        
        - Limit who can view an employee's skills.
    """,

    'author': "Penguin Infrastructure",
    'maintainers': ['David Páez'],
    'website': "https://penguin.digital",
    'category': 'Human Resources',
    'version': '18.0.1.0.0',
    'license': "OPL-1",

    'depends': ['base', 'account', 'web', 'hr'],

    "data": [
        "views/hr_views.xml",
    ],

    'i18n': ['i18n/es.po'],
}

