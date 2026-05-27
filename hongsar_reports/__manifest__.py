# -*- coding: utf-8 -*-
{
    'name': 'Hongsar Formal Reports',
    'version': '18.0.1.0.2',
    'category': 'Accounting/Reporting',
    'summary': 'Formal Myanmar-ready custom Sales Order and Invoice reports',
    'description': """
Hongsar Formal Reports
======================

Provides standalone formal PDF reports for:
- Sales Order / Quotation
- Customer Invoice / Credit Note

Features:
- Modern formal layout with clear table grid lines
- Company logo and structured address blocks
- Myanmar Unicode compatible PDF rendering
- Parallel-safe rollout with separate report actions
    """,
    'author': 'Custom',
    'depends': ['base', 'web', 'sale', 'account', 'hongsar_internal_mod'],
    'data': [
        'data/report_paperformat.xml',
        'reports/report_layout.xml',
        'reports/report_saleorder.xml',
        'reports/report_invoice.xml',
        'reports/report_actions.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'hongsar_reports/static/src/scss/report_style.scss',
        ],
    },
    'external_dependencies': {
        'python': ['weasyprint'],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
