# -*- coding: utf-8 -*-
{
    'name': "Odoo 19 Features Backport",

    'summary': "Backported features from Odoo 19 to Odoo 18",

    'description': """
        This module brings select Odoo 19 features to Odoo 18:
        
        - Add a server action to create users in bulk from selected employees.
    """,

    'author': "Penguin Infrastructure",
    'maintainers': ['José González'],
    'website': "https://penguin.digital",
    'category': 'Tools',
    'version': '18.0.1.0.0',
    'license': "OPL-1",

    'depends': ['base', 'hr'],

    "data": [
        "views/hr_employee_views.xml"
    ]
    
}
