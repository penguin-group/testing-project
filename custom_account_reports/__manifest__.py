#pylint: disable=pointless-statement,missing-module-docstring

{
    'name': "Reportes de Contabilidad Perzonalizados",

    'summary': """
        Perzonaliza los reportes de contabilidad tanto para el 
        archivo generado en PDF como el archivo generado en XLSX
    """,

    'description': """
        Perzonaliza los reportes de contabilidad tanto para el 
        archivo generado en PDF como el archivo generado en XLSX
    """,

    'author': "Giuliano Díaz",
    'website': "https://www.giulianodiaz.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '17.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_reports'],

    # always loaded
    'data': [
        'views/show_primary_color_field.xml',
        'views/custom_account_reports_pdf.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}
