# -*- coding: utf-8 -*-
{
    'name': "Paraguay - Accounting",

    'summary': "This module adds accounting features to the Paraguayan localization.",

    'description': """
        This module adds the following accounting features to the Paraguayan localization:
        * VAT Purchase Book (xlsx report)
        * VAT Sale Book (xlsx report)
    """,

    'author': "Penguin Infrastructure, José González",
    'website': "https://penguin.digital",
    'category': 'Accounting',
    'version': '17.0.1.1.1',

    'depends': ['base', 'account', 'report_xlsx'],

    'data': [
        'security/ir.model.access.csv',
        'wizards/report_vat_purchase_views.xml',
        'wizards/report_vat_sale_views.xml'
    ],
    'i18n': ['i18n/es.po'],
}

