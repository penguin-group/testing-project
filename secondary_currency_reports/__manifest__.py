{
    'name' : 'Secondary Currency Accounting Reports',
    'summary': 'View and create reports',
    'category': 'Accounting/Accounting',
    'description': """
Secondary Currency Accounting Reports
====================================
    """,
    'author': "Penguin Infrastructure, William Eckerleben",
    'website': "https://penguin.digital",
    'license': "OPL-1",
    'depends': ['secondary_currency'],
    'data': [
        'data/multicurrency_revaluation_report.xml',
        
        'wizard/multicurrency_revaluation.xml',
    ],
    'version': '18.0.0.1',
    'assets': {
        'web.assets_backend': [
            'secondary_currency/static/src/components/**/*',
        ],
    },
}
