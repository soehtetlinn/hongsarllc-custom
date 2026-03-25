# -*- coding: utf-8 -*-
{
    'name': 'Product Default Code Generator',
    'version': '18.1',
    'category': 'Product',
    'summary': 'Auto-generate default_code based on category, creator, and sequence',
    'description': """
Product Default Code Generator
==============================

This module automatically generates the default_code (Internal Reference) for products
based on:
* Category initials (excluding "All")
* Creator initials (first 2 characters of create_uid.name)
* Sequential number (001, 002, etc.)

Format: CSM_Tu001
- CSM: Category initials (e.g., "All / Courses / SAT / Maths" → "CSM")
- Tu: User initials (e.g., "tutor1" → "tu")
- 001: Sequence number based on category + creator combination

Example:
--------
Category: "All / Courses / SAT / Maths" → CSM
Creator: "tutor1" → tu
Sequence: First product → 001
Result: CSM_Tu001

Author: Custom Development
    """,
    'author': 'Soe Htet Linn',
    'depends': ['product'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

