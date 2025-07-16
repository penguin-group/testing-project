{
    "name": "Email Notification",
    "summary": "Implement a notification workflow depending on purchase orders' total amount.",
    "version": "18.0.1.0.0",
    "website": "https://penguin.digital",
    "author": "David Páez",
    "application": False,
    "installable": True,
    "depends": ["mail", "hr", "purchase"],
    "data": [
        "security/ir.model.access.csv",
        "data/email_template.xml",
        "views/po_mail_notification_view.xml",
        # "views/tier_review_view.xml",
        # "views/tier_validation_exception_view.xml",
        # "templates/tier_validation_templates.xml",
    ]
}
