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
    'version': '18.0.0.1',
    'license': "OPL-1",
    'depends': ['accountant','secondary_currency'],
    'data': [
        'security/ir.model.access.csv',

        'data/secondary_currency_multicurrency_revaluation_report.xml',
        'data/secondary_currency_report_actions.xml',
        'data/menuitems.xml',

        'wizard/multicurrency_revaluation.xml',
    ],
}
