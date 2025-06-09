# -*- coding: utf-8 -*-
{
    'name': "Paraguay - Accounting",

    'summary': "This module adds accounting features to the Paraguayan localization.",

    'description': """
        This module adds the following accounting features to the Paraguayan localization:
        * VAT number unique for customers and suppliers
        * Invoice Authorization
        * Self-printed Invoices
        * VAT Purchase Book (xlsx report)
        * VAT Sale Book (xlsx report)
    """,

    'author': "Penguin Infrastructure, José González",
    'website': "https://penguin.digital",
    'category': 'Accounting',
    'version': '18.0.1.0.1',
    'license': "OPL-1",

    'depends': ['base', 'account', 'web'],

    "data": [
        'data/email_template.xml',
        "data/service_cron.xml",
        "security/account_security.xml",
        "security/book_registration_security.xml",
        "security/ir_ui_menu_security.xml",
        "security/ir.model.access.csv",
        "views/account_account.xml",
        "views/account_journal_views.xml",
        "views/account_move_views.xml",
        "views/book_registration_report_views.xml",
        "views/book_registration_views.xml",
        "views/hr_expense_views.xml",
        "views/invoice_authorization_views.xml",
        "views/invoice_controller_templates.xml",
        "views/menu_item.xml",
        "views/res_config_settings_views.xml",
        "views/res_currency_views.xml",
        "views/res_partner.xml",
        "views/hr_expense_views.xml",
        "wizards/invoice_cancel_views.xml",
        "wizards/invoice_edit_currency_rate_views.xml",
        "wizards/report_res90_views.xml",
        "wizards/report_vat_purchase_views.xml",
        "wizards/report_vat_sale_views.xml",
        "data/ir_config_parameter.xml",
    ],


    'demo': [
        'demo/res_partner_demo.xml',
        'demo/invoice_authorization_demo.xml',
        'demo/account_journal_demo.xml'
    ],
    'i18n': ['i18n/es.po'],
    'assets': {
        'web.assets_backend': [
            'l10n_py/static/src/webclient/company_service.js',
        ],
    },
}

