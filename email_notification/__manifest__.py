{
    "name": "Email Notification",
    "summary": "Implements a notification workflow based on conditions set by the user.",
    "version": "18.0.1.0.0",
    "website": "https://penguin.digital",
    "author": "David Páez",
    "application": False,
    "installable": True,
    "depends": ["mail", "hr", "purchase"],
    "data": [
        "security/ir.model.access.csv",
        "data/email_template_purchase_order.xml",
        "views/po_mail_notification_view.xml"
    ]
}
