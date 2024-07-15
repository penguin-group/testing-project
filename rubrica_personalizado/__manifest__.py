# -*- coding: utf-8 -*-
{
    'name': "rubrica_personalizado",

    'summary': """
        Modulo para registro de rúbricas
        """,

    'description': """
        Modulo personalizado para rúbricas
        Tarea N° 19.296 - se crea un modulo personalizado de rubrica, ya que la opcion de diario
        no esta aceptando caracteres especiales.
        Tarea N°22.733 - se verifica que no tiene condicion en el caso de que no tenga adjuntado la 
        imagen de rubrica
        Tarea N°22.734 - se procede a agregar a los textos la opcion de unidecode para que pueda aceptar
        ciertos caracteres en el reporte.

        

    """,

    'author': "Interfaces S.A., Edgar Gonzalez",
    'website': "http://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Account',
    'version': '17.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'interfaces_rubrica'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
