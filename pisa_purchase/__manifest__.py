# -*- coding: utf-8 -*-
{
    'name': "PISA Purchase",

    'summary': "Customized features for PISA in the purchase application.",

    'description': """
        Customized features for PISA in the purchase application.
    """,

    'author': "Penguin Infrastructure S.A.",
    'mantainers': ['José González'],
    'website': "https://penguin.digital",

    'category': 'Accounting',
    'version': '18.0.1.0.0',
    'license': "OPL-1",

    'depends': ['base', 'purchase_tier_validation', 'purchase_request_tier_validation', 'project'],

    'data': [
        'views/purchase_views.xml',
        'views/purchase_request_views.xml',
    ],
}
