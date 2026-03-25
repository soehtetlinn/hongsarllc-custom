# -*- coding: utf-8 -*-
{
    'name': 'SendGrid Email Integration',
    'version': '18.0.1.0.0',
    'category': 'Mail',
    'summary': 'Send emails via SendGrid API (bypasses SMTP blocking)',
    'description': """
SendGrid Email Integration for Odoo 18
=====================================

This module integrates SendGrid HTTP API with Odoo, bypassing SMTP port blocking
on cloud providers like Digital Ocean.

Features:
---------
* Send emails via SendGrid HTTP API (port 443)
* Bypass SMTP port 25/587/465 blocking
* Support for verified senders
* Easy configuration
* Better deliverability than traditional SMTP

Setup:
------
1. Get SendGrid API Key from https://app.sendgrid.com/
2. Verify your sender email
3. Configure in Settings → Technical → System Parameters
4. Test and start sending emails!

Author: Custom Development
    """,
    'author': 'Ten Ten Tutor',
    'website': 'https://sendgrid.com',
    'depends': ['mail'],
    'data': [
        'views/ir_mail_server_views.xml',
        'data/system_parameters.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

