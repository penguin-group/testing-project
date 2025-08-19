# -*- coding: utf-8 -*-
{
    "name": "Expenses Flow",
    "summary": "Change the behavior of the expenses",
    "description": """
        This module changes the behavior of the expenses as follows:
        - Paid by Company
            - Expense Report generates a vendor bill (in draft) for each expense line 
              using the journal set in the expense settings page. The journal entry credits the
              reimbursement account (configured in the expense settings page).
            - For each expense line, a clearing journal entry is created and confirmed. 
              It debits the reimbursement account
              and credits the Expense Outstanding Account (also configured in the expense settings page). 
              If the expense exceeds the amount available in the Expense Outstanding Account, 
              a separate line will be added to the journal entry for the reimbursement account 
              crediting the exceeded amount.
        - Paid by Employee
            - Expense Report generates a vendor bill (in draft) for each expense line
              using the journal set in the expense settings page. The journal entry credits the
              reimbursement account (configured in the expense settings page) to the Vendor.
            - For each expense line, a clearing journal entry is created and confirmed. 
              It debits the reimbursement account to the Vendor and credits the reimbursement 
              account to the Employee.
        - Petty Cash
            - We added a new option to the "Paid by" field in the expense form view,
              which allows you to select "Petty Cash". This option will allow the user to select a
              petty cash account to pay the expense. The petty cash possible values are taken from the
              employee's department page.
        - Advanced User Features
            - Added a new user group "Advanced User" that allows (only for expenses paid by employee or company):
                - Create expenses for all employees in the same company
                - Access to expenses where the user is the expense creator or the selected employee
    """,
    "author": "Penguin Infrastructure S.A.",
    "maintainers": ["José González"],
    "website": "https://penguin.digital",
    "category": "Expenses",
    "version": "18.0.1.2.0",
    "license": "OPL-1",
    "depends": ["hr_expense", "account_asset"],
    "data": [
        "data/account_chart.xml",
        "security/hr_expense_security.xml",
        "security/ir_rule.xml",
        "views/res_config_settings_views.xml",
        "views/hr_expense_views.xml",
        "views/hr_department_views.xml",
        "report/hr_expense_report.xml",
    ],
}
