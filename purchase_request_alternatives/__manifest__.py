# -*- coding: utf-8 -*-
{
    'name': "Purchase Request - Alternatives",

    'summary': "Adds RFQ's alternatives compatiblity to the purchase request module",

    'description': """
        This module adds the relationship between RFQ's alternatives and the Purchase Request
    """,

    'author': "Penguin Infrastructure S.A.",
    'mantainers': ['José González'],
    'website': "https://penguin.digital",

    'category': 'Purchase',
    'version': '18.0.1.0.0',
    'license': "OPL-1",

    'depends': ['purchase_requisition', 'purchase_request'],

    'data': [
        'views/purchase_views.xml',
    ],
}