# -*- coding: utf-8 -*-
{
    'name': "rrhh_personalizado",

    'summary': """
        Recibo de salario formato ministerio de trabajo
        """,

    'description': """
        tarea N° 19.533 - se crea recibo de salario en formato del ministerio de trabajo
        Tarea N° 19.535 -  se modifican recibo de vacaciones y notificacion de vacaciones
        25896: El cliente solicita que el salario imponible corresponda al salario total + haberes y salario real el que figura en el contrato.
    """,

    'author': "Interfaces S.A. - Edgar Gonzalez",
    'website': "https://www.interfaces.com.py",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'rrhh_payroll', 'rrhh_liquidacion', 'ips_rei_hr_payslip'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/hr_payroll.xml',
        'views/hr_attendance.xml',
        'report/hr_payroll.xml',
        'report/notificacion_vacacion_comunicacion.xml',
        'report/notificacion_vacacion_recibo.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
