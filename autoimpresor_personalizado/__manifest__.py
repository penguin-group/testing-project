# -*- coding: utf-8 -*-
{
    'name': "autoimpresor_personalizado",

    'summary': """
        Comentario en Factura
        """,

    'description': """
        1. Se modifica el diseño de la factura autoimpresor, según requerimiento del cliente
        Segun tarea N°19.295, se procedio a agregar a algunos campos mecionado en la tarea como campos requeridos, de modo
        a que no le deje guardar si no esta completadas.
        Segun tarea N°19.282 se procedio a agregar un nuevo tab en la configuracion de la compañia para que puedan agregar
        los datos de las cuentas bancarias de modo a que esos datos se llaman y aparescan en el codigo QR dento de la factura, asi tambien
        para eso se crea un nuevo campo en la tabla de res_company con el nombre de datos_banco.
        -Se sobrescribe validacion de formato de comprobante en account_move tipo in_invoice, solo controlara el formato 
        cuando sea del tipo 2 proveedores nacionales en el campo de diario.


    """,

    'author': "Interfaces S.A. - Edgar Gonzalez",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.1.0',

    # any module necessary for this one to work correctly
    'depends':['base','account', 'factura_autoimpresor', 'proveedores_timbrado'],

    # always loaded
    'data': [
        'views/factura.xml',
        'views/datos_banco.xml',
        'views/account_move.xml',
    ],

}
