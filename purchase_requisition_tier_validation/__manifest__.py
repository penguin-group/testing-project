# -*- coding: utf-8 -*-
{
    'name': "Purchase Requisition Tier Validation",

    'summary': "Extends the functionality of Purchase Requisition (Purchase Agreements) to support a tier validation process.",

    'author': "Penguin Infrastructure",
    'maintainers': ['José González'],
    'website': "https://penguin.digital",
    'category': 'Purchases',
    'version': '18.0.1.0.0',
    'license': "OPL-1", 

    'depends': ['purchase_requisition', 'base_tier_validation'],

    'data': [
        'views/purchase_requisition_views.xml',
    ],
}
