# -*- coding: utf-8 -*-
{
    "name": "Base Tier Validation HR",
    "summary": "Allow Employee Role in Tier Definition",
    "description": """
        This module allows the Employee Role to be used in the Tier Definition model.
    """,
    "author": "Penguin Infrastructure S.A.",
    "mantainers": ["José González"],
    "website": "https://penguin.digital",
    "category": "Tools",
    "version": "18.0.1.0.0",
    "license": "OPL-1",
    "depends": ["base_tier_validation","hr"],
    "data": [
        'views/tier_definition_view.xml'
    ],
}