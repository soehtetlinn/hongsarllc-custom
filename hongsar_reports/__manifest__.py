# -*- coding: utf-8 -*-
{
    'name': 'Hongsar Formal Reports',
    'version': '18.0.2.0.0',
    'category': 'Accounting/Reporting',
    'summary': 'Formal Myanmar-ready custom Sales Order and Invoice reports with WeasyPrint',
    'description': """
Hongsar Formal Reports
======================

Provides standalone formal PDF reports for:
- Sales Order / Quotation
- Customer Invoice / Credit Note

Features:
- Classic formal layout with clear table grid lines
- Company logo and structured address blocks
- WeasyPrint PDF engine for proper Myanmar Unicode rendering
- Automatic fallback: uses WeasyPrint when Myanmar text detected, wkhtmltopdf otherwise
- Pyidaungsu font support

Requirements:
- pip install weasyprint
    """,
    'author': 'Custom',
    'depends': ['base', 'web', 'sale', 'account', 'hongsar_internal_mod'],
    'data': [
        'data/report_paperformat.xml',
        'reports/report_assets.xml',
        'reports/report_common_styles.xml',
        'reports/report_layout.xml',
        'reports/report_saleorder.xml',
        'reports/report_invoice.xml',
        'reports/report_actions.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'hongsar_reports/static/src/css/report_fonts.css',
            'hongsar_reports/static/src/scss/report_style.scss',
        ],
        'web.report_assets_pdf': [
            'hongsar_reports/static/src/css/report_fonts.css',
            'hongsar_reports/static/src/scss/report_style.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
