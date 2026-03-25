# -*- coding: utf-8 -*-
{
    'name': 'Report Myanmar Font Fix',
    'version': '18.0.2.0.0',
    'category': 'Hidden',
    'summary': 'Fix Myanmar/Burmese Unicode text rendering in PDF reports',
    'description': """
Report Myanmar Font Fix
=======================

Fixes broken Myanmar Unicode text in PDF reports.

Problem:
--------
wkhtmltopdf cannot properly render Myanmar Unicode text due to missing complex 
text shaping (HarfBuzz) support. This causes text like "ကြက်သွန်နီကြော်ဗူး" to 
appear as garbled characters in PDF output.

Solution:
---------
This module uses WeasyPrint instead of wkhtmltopdf when Myanmar text is detected.
WeasyPrint has proper HarfBuzz support and renders Myanmar Unicode correctly.

Requirements:
-------------
- Python package: weasyprint (pip install weasyprint)
- System fonts: Noto Sans Myanmar or Padauk (usually pre-installed on Ubuntu)

Usage:
------
Simply install this module. It automatically fixes all PDF reports containing Myanmar text.
    """,
    'author': 'Custom',
    'depends': ['base', 'web'],
    'data': ['views/report_templates.xml'],
    'external_dependencies': {
        'python': ['weasyprint'],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
