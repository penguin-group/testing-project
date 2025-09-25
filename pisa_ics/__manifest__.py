{
    'name': "Pisa ICS",

    'summary': """Infrastructure Control System""",

    'description': """Pisa ICS - Infrastructure Control System""",

    'author': "Penguin Infrastructure S.A. - DCD",
    'maintainers': ['Dani Sanchez', 'Elias Gonzalez'],
    'website': "https://penguin.digital",
    'category': 'Custom',
    "license": "OPL-1",
    'version': '18.0.0.1',
    'depends': [
        'base',
    ],

    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
    ],

    'installable': True,
}
