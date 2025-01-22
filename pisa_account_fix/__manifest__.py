# -*- coding: utf-8 -*-
{
    'name': "Journal Entries Fix",
    'summary': "This module adds a server action in the account move to fix the invoice currency rate field in Odoo.",
    'description': """
        This module introduces a server action within the account move model, 
        enabling users to quickly and efficiently correct the currency rate 
        applied to their invoices.    
    """,
    'author': "Penguin Infrastructure, José González",
    'website': "https://penguin.digital",
    'category': 'Accounting',
    'version': '18.0.1.0',
    'license': "OPL-1",
    'depends': ['account'],
    'data': [
        'data/cron.xml',
        'views/account_move_views.xml',
    ],
    'demo': [
    ],
}

