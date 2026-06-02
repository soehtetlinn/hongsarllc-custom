# -*- coding: utf-8 -*-
{
    'name': 'Hongsar Org Reports Fix',
    'version': '18.0.1.3.1',
    'category': 'Reporting',
    'summary': 'Myanmar report fonts and Sale Order report layout fixes',
    'description': """
- Pyidaungsu font on all PDF/HTML reports
- Sale Order (standard Odoo report): No., Other Name, Pkg Qty; taxes removed; black SO number

Pyidaungsu fonts are embedded as base64 in the CSS for wkhtmltopdf compatibility.
Run generate_font_css.py to regenerate if fonts are updated.
    """,
    'author': 'Custom',
    'depends': ['web', 'sale', 'hongsar_internal_mod'],
    'data': [
        'views/report_assets.xml',
        'views/sale_report_templates.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'hongsar_org_reports_fix_mod/static/src/css/org_reports_fix.css',
        ],
        'web.report_assets_pdf': [
            'hongsar_org_reports_fix_mod/static/src/css/org_reports_fix.css',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
