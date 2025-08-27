{
    "name": "PISA Agreement Management",
    "summary": "Implements agreement management.",
    "version": "18.0.1.0.0",
    "website": "https://penguin.digital",
    'author': "Penguin Infrastructure",
    'maintainers': ['David Páez'],
    "application": True,
    "installable": True,
    "depends": ["base", "web", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/pisa_agreement_views.xml",
        "views/agreement_type_views.xml",
        "views/agreement_stage_views.xml",
        "views/legal_process_type_views.xml",
        "views/pisa_agreement_menu_views.xml",
    ]
}
