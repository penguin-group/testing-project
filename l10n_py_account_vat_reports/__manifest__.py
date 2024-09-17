# -*- coding: utf-8 -*-
{
    'name': "PY VAT Reports",

    'summary': "Purchase and Sale VAT reports",

    'description': """
        Purchase and Sale VAT reports
    """,

    'author': "Penguin Infrastructure, José González",
    'website': "https://penguin.digital",
    'category': 'Accounting',
    'version': '17.0.1.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'interfaces_timbrado', 'report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/report_vat_purchase_views.xml',
        'wizards/report_vat_sale_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

