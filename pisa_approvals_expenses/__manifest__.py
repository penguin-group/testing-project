{
    "name": "PISA Approval Expenses",
    "summary": "Adds bank and currency fields to approval types and creates a bill for employee advancement.",
    "version": "18.0.1.0.0",
    'license': "OPL-1",
    "website": "https://penguin.digital",
    'author': "Penguin Infrastructure",
    'maintainers': ['David Páez'],
    "application": False,
    "installable": True,
    "depends": ["approvals", "hr_expense_flow"],
    "data": [
        "views/approval_category_views.xml",
        "views/approval_request_views.xml",
        "views/account_move_views.xml",
        "views/hr_expense_sheet_views.xml",
    ]
}
