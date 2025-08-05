# -*- coding: utf-8 -*-
{
    'name': "PISA HR Payroll",

    'summary': "Paraguayan Payroll Localization for Penguin Infrastructure",

    'description': """
        Module for Paraguayan payroll processing with local regulations compliance.
        
        This module provides:
        * Paraguayan salary structures and rules
        * IPS (Social Security) calculations  
        * Local allowances and deductions
        * Family allowances (Bonificación Familiar)
        * Daycare allowances (Guardería)
        * Overtime calculations with night surcharges
        * Holiday work calculations
        * Medical leave processing
        * Vacation pay calculations
        * Court garnishments (Embargo Judicial)
        * Paraguayan payslip reports
        * Integration with l10n_py accounting localization
    """,

    'author': "Penguin Infrastructure",
    'website': "https://penguin.digital",
    'category': 'Human Resources/Payroll',
    'version': '18.0.1.0.0',
    'license': "OPL-1",

    'depends': [
        'base', 
        'hr', 
        'hr_payroll',
        'hr_work_entry_contract',
        'l10n_py',
        'account'
    ],

    "data": [
        # Security
        "security/ir.model.access.csv",
        
        # Data
        "data/hr_salary_rule_category_data.xml",
        "data/hr_payroll_structure_type_data.xml", 
        "data/hr_payroll_structure_data.xml",
        "data/hr_payslip_input_type_data.xml",
        "data/hr_rule_parameter_data.xml",
        "data/hr_salary_rule_data.xml",
        
        # Views
        "views/hr_employee_views.xml",
        "views/hr_contract_views.xml", 
        "views/hr_payslip_views.xml",
        "views/hr_payroll_menus.xml",
        
        # Reports
        "reports/hr_payslip_report.xml",
        "reports/report_payslip_py.xml",
    ],

    'demo': [
        # 'demo/demo.xml',
    ],
    
    'i18n': ['i18n/es.po'],
    
    'installable': True,
    'application': False,
    'auto_install': False,
}