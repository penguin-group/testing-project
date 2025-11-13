# -*- coding: utf-8 -*-
{
    "name": "Website Salary Attachment Request",
    "version": "18.0.1.0.0",
    "summary": "Website form to request salary attachments with employee defaults",
    "author": "Penguin Infrastructure",
    "maintainers": ["William Eckerleben"],
    'website': "https://www.pengin.digital",
    "category": "Human Resources",
    "license": "OPL-1",
    "depends": ["website", "portal", "hr", "hr_payroll", "l10n_py_hr_payroll"],
    "data": [
        "views/website_templates.xml",
        "views/portal_templates.xml",
        "views/hr_salary_attachment_views.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_salary_attachment_request/static/src/js/sa_form.js",
        ],
    },
    "installable": True,
}
