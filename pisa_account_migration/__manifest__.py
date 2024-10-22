# -*- coding: utf-8 -*-
{
    'name': "Data Migration",

    'summary': "Data migraton from interfaces addons to the new l10n_py addon fields.",

    'description': """
        Data migraton from interfaces addons to the new l10n_py addon fields.
    """,

    'author': "Penguin Infrastructure, José González",
    'website': "https://penguin.digital",

    'category': 'Accounting',
    'version': '17.0.1.1.1',

    'depends': ['base', 'account', 'pisa_account'],

    # always loaded
    'data': [
        'data/ir_cron.xml',
    ],
}

