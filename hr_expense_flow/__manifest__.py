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
            - For each expense line, a journal entry is created and confirmed. It debits the reimbursement account
              and credits the Expense Outstanding Account (also configured in the expense settings page). 
              If the expense exceeds the amount available in the Expense Outstanding Account, 
              a separate line will be added to the journal entry for the reimbursement account 
              crediting the exceeded amount.
    """,
    "author": "Penguin Infrastructure S.A.",
    "mantainers": ["José González"],
    "website": "https://penguin.digital",
    "category": "Expenses",
    "version": "18.0.1.0.0",
    "license": "OPL-1",
    "depends": ["hr_expense"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/hr_expense_views.xml",
    ],
}
