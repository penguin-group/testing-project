# -*- coding: utf-8 -*-
{
    'name': "Completion Certificates Tier Validation",

    'summary': "Extends the functionality of Completion Certificates to support a tier validation process.",

    'author': "Penguin Infrastructure",
    'maintainers': ['José González'],
    'website': "https://penguin.digital",
    'category': 'Purchases',
    'version': '18.0.1.0.0',
    'license': "OPL-1", 

    'depends': ['completion_certificates', 'base_tier_validation'],

    'data': [
        'views/certificate_views.xml',
    ],
}
