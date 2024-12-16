#pylint: disable=pointless-statement,missing-module-docstring

{
    'name': "Custom Properties for Product Categories",

    'summary': """
        Add custom properties to product categories and 
        ensures that all products in a category share these properties.
    """,

    'description': """
        This module extends product categories to include properties 
        personalized. Products associated with a category will inherit 
        automatically these properties.
    """,

    'author': "Penguin Academy",
    'website': "penguin.software",

    'category': 'Inventory',
    "license": "LGPL-3",
    'version': '17.0.1.0',

    'depends': ['base', 'product', 'stock'],

    'data': [
        'views/product_template_category_properties_view.xml',
        'views/stock_lock_view.xml',
        'data/warehouse_data.xml',
        'data/product_category_data.xml'
    ],
    'post_init_hook': '_post_init_hook', 

    'demo': [],
    'installable': True,
    'application': True,
}
