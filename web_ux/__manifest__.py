# -*- coding: utf-8 -*-
{
    'name': 'Web UX Enhancements',
    'version': '18.0.1.0.0',
    'category': 'Hidden/Tools',
    'summary': 'Chatter position control and sticky list columns',
    'description': """
Web UX Enhancements
===================
* Chatter Position: Move chatter beside (aside) or down (below) form - user preference
* Sticky Columns: Keep first columns fixed when scrolling horizontally in list views
    """,
    'depends': ['web', 'mail', 'base_setup'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'web_ux/static/src/form_compiler_patch.js',
            'web_ux/static/src/form_renderer_patch.js',
            'web_ux/static/src/form_controller_patch.js',
            'web_ux/static/src/mail_form_renderer_patch.js',
            'web_ux/static/src/list_renderer_patch.js',
            'web_ux/static/src/views/list_renderer.xml',
            'web_ux/static/src/list_sticky_columns.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
