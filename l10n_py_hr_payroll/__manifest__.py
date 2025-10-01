# -*- coding: utf-8 -*-
{
    'name': "Paraguay HR Payroll",

    'summary': "Paraguayan Payroll Localization",

    'description': """
        Streamlined Paraguayan payroll using native Odoo features and salary attachments.
        
        This module provides:
        * Paraguay-specific salary structures and rules
        * IPS (Social Security) calculations and reporting
        * Salary attachment integration for recurring deductions/allowances
        * Overtime calculations with night surcharges  
        * Holiday and vacation pay calculations
        * Simplified payroll management
        * Paraguayan payslip reports
        * Integration with l10n_py accounting localization
        
        Key Benefits:
        * Uses native Odoo salary attachments (maintainable)
        * Leverages standard time-off system
        * Clean contract management without clutter
        * Future-proof against Odoo upgrades
    """,

    'author': "Penguin Infrastructure S.A.",
    'maintainers': ["William Eckerleben"],
    'website': "https://penguin.digital",
    'category': 'Human Resources/Payroll',
    'version': '18.0.1.0.0',
    'license': "OPL-1",

    'depends': [
        'base', 
        'hr', 
        'hr_payroll',
        'hr_payroll_account',
        'hr_work_entry_contract',
        'l10n_py',
        'account'
    ],

    "data": [
        # Security
        "security/ir.model.access.csv",
        
        # Data
        "data/account_journal_data.xml",
        "data/hr_salary_rule_category_data.xml",
        "data/hr_payroll_structure_type_data.xml", 
        "data/hr_payroll_structure_data.xml",
        "data/hr_payslip_input_type_data.xml",
        "data/hr_rule_parameter_data.xml",
        "data/hr_salary_rule_data.xml",
        
        # Views
        "views/hr_contract_views.xml",
        "views/hr_payroll_structure_views.xml",
        "views/hr_salary_attachment_views.xml",
        "views/res_config_settings_views.xml",
        "views/hr_employee_views.xml",
        "views/res_company_views.xml",
        'views/hr_job_views.xml',

        "views/report_payslip_templates.xml",
    ],

    'demo': [
        # 'demo/demo.xml',
    ],
    
    'i18n': ['i18n/es.po'],
    
    'installable': True,
    'application': False,
    'auto_install': False,
}