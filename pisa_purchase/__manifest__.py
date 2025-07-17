# -*- coding: utf-8 -*-
{
    'name': "PISA Purchase",

    'summary': "Customized features for PISA in the purchase application.",

    'description': """
        Customized features for PISA in the purchase application.
    """,

    'author': "Penguin Infrastructure S.A.",
    'mantainers': ['José González', 'David Páez'],
    'website': "https://penguin.digital",

    'category': 'Accounting',
    'version': '18.0.1.2.0',
    'license': "OPL-1",

    'depends': ['base', 'purchase_requisition', 'purchase_tier_validation', 'purchase_request_tier_validation', 'completion_certificates', 'project', 'account', 'purchase_request'],

    'data': [
        'security/purchase_security.xml',
        'views/purchase_views.xml',
        'views/purchase_request_views.xml',
        'views/menu_override.xml',
    ],
}
