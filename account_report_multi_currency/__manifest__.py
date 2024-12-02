{
    'name': 'Account Reports Multi Currency',
    'version': '17.0.1.0',
    'license': 'OPL-1',
    'category': 'Accounting/Accounting',
    'author': 'Penguin Infrastructure',
    'website': 'https://penguin.digital',
    'summary': '''
Multi Currency in Accounting Reports.
Financial Report
Account Report
Multi Currency Financial Report
Accounting Reports.
    ''',
    'description': '''
Account Reports Multi Currency module is used to print account financial reports in mentioned currency.
    ''',
    'depends': ['account_reports'],
    'data': [
        # 'views/account_report_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_report_multi_currency/static/src/components/**/*',
        ],
    },
    'images': [],
    'installable': True,
}
