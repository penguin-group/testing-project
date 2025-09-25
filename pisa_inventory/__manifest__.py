#pylint: disable=pointless-statement,missing-module-docstring

{
    'name': "Pisa Inventory to Manage Miners' Operations",

    'summary': """
        Add Pisa inventory to product categories and 
        ensures that all products in a category share these properties.
    """,

    'description': """
        This module extends product categories to include personalized 
        properties. Products associated with a category will automatically 
        inherit these properties.
    """,

    'author': "Penguin Infrastructure S.A.",
    'maintainers': ['Dani Sanchez', 'Elias Gonzalez'],
    'website': "https://penguin.digital",

    'category': 'Inventory',
    "license": "OPL-1",
    'version': '18.0.0.1',

    'depends': ['base', 'product', 'stock'],

    'data': [
        'views/product_template_category_properties_view.xml',
        'views/stock_lock_view.xml',
        'data/warehouse_data.xml',
        'data/product_category_data.xml'
    ],
    'post_init_hook': '_post_init_hook', 
    

    'i18n' : ['i18n/es.po'],
    'installable': True,
}
