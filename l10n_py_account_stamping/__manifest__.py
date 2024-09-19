# -*- coding: utf-8 -*-
{
    'name': "PY Stamping",

    'summary': "Implements the stamping (invoice authorization numbers) functionality.",

    'description': """
        Implements the stamping (invoice authorization numbers) functionality.    
    """,

    'author': "Penguin Infrastructure, José González",
    'website': "https://www.penguin.digital",

    'category': 'Accounting',
    'version': '17.0.1.1',

    'depends': ['base', 'account'],

    'data': [
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

