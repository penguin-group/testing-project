# -*- coding: utf-8 -*-
{
    'name': "PISA Purchase",

    'summary': "Customized features for PISA in the purchase application.",

    'description': """
        Customized features for PISA in the purchase application.
    """,

    'author': "Penguin Infrastructure, José González",
    'website': "https://penguin.digital",

    'category': 'Accounting',
    'version': '18.0.1.0.0',
    'license': "OPL-1",

    'depends': ['base', 'purchase'],

    'data': [
        'security/ir.model.access.csv',
        'security/certificate_security.xml',
        'views/purchase_views.xml',
        'views/purchase_certificate_views.xml',
    ],

    'demo': [
    ],

    # 'i18n': ['i18n/es.po'],
}

