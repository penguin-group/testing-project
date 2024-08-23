# -*- coding: utf-8 -*-
{
    'name': "Consolidation Automation",
    'summary': "Automatically manage and update consolidated accounts based on account prefixes",
    'description': """
        This module automates the management of consolidated accounts by ensuring that all relevant accounts,
        based on specified prefixes, are included in the respective consolidated account. The module introduces 
        a scheduled action that periodically checks all consolidated accounts, searches for accounts in the system 
        that match the given prefixes, and includes any missing accounts. This ensures that consolidated accounts 
        are always up-to-date, saving time and reducing manual effort.
    """,
    'author': "Penguin",
    'website': "https://penguin.software",
    'category': 'Accounting',
    'version': '17.0.0.1',
    'depends': ['base', 'account_consolidation'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/consolidation_coa_views.xml',
        'data/cron_consolidated_accounts.xml'
    ],
    'demo': [
        'demo/demo.xml',
    ],
}

