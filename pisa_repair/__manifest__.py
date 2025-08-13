# pylint: disable=pointless-statement,missing-module-docstring

{
    'name': "Pisa Repair for miners",

    'summary': """
        Customize repair statuses and kanban view for better tracking and management of repair processes.
    """,

    'description': """
        Pisa Repair for miners. This module extends the functionality of the standard repair module in Odoo to better suit the needs of mining operations. It includes custom statuses for repair orders, enhanced kanban views for better visualization of the repair process, and additional fields to capture relevant information specific to mining equipment repairs.
    """,

    'author': "Penguin Infrastructure S.A.",
    'maintainers': ['Dani Sanchez', 'Elias Gonzalez'],
    'website': "https://penguin.digital",
    'category': 'Repair',
    "license": "OPL-1",
    'version': '18.0.0.1',
    'depends': [
        'base',
        'repair',
        'stock',
        'sale',
        'sales_team',
        'helpdesk',
        'queue_job'
    ],

    'data': [
        'security/custom_roles_security.xml',      
        'security/ir.model.access.csv',
        'data/repair_fault_data.xml',
        'data/repair_initial_state_data.xml',
        'data/repair_tags_data.xml',
        'data/repair_final_resolution_data.xml',
        'data/repair_replaced_components_data.xml',
        'data/repair_steps_data.xml',         
        'data/repair_external_service.xml',  
        'data/repair_orders_job.xml',              
        'views/repair_steps_views.xml',
        'views/repair_order_form_tab_noc_view.xml',
        'views/repair_order_form_tab_mining_view.xml',
        'views/repair_order_customizations.xml',
        'views/repair_order_kanban_view.xml',
        'views/repair_order_list_view_custom.xml',
        'views/sale_order_line_view.xml',
        'views/repair_menu.xml',
        'views/repair_fault_list_view.xml',
        'views/repair_initial_state_view.xml',
        'views/repair_order_form_tab_customizations.xml',
        'views/custom_search_views.xml',
        'views/repair_replaced_components_view.xml',
        'views/repair_final_resolution_view.xml',
        'views/repair_external_service_view.xml',
        'views/portal_sale_order.xml',
        'views/product_product_tree_view.xml',
        'reports/saleorder_report.xml', 
        'wizards/consolidate_quotations_view.xml',
        'wizards/ticket_validation_views.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'pisa_repair/static/src/js/repair_order_chatter_timer.js',
            'pisa_repair/static/src/js/ticket_validation.js',
        ],
    },

    'i18n' : ['i18n/es.po'],
    'installable': True,
}
