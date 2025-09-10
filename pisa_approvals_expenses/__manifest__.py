{
    "name": "PISA Approval Expenses",
    "summary": "Approvals",
    "version": "18.0.1.0.0",
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
    ]
}
