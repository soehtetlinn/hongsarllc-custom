# -*- coding: utf-8 -*-
{
    'name': 'Payment Stripe Enhanced - Webhook Error Handling',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'Enhanced error handling and fallback mechanisms for Stripe webhooks',
    'description': """
Enhanced Stripe Webhook Error Handling
======================================
This module provides:
* Comprehensive error handling for Stripe webhooks
* Retry mechanism for failed webhook processing
* Detailed logging and monitoring
* Fallback mechanisms for webhook processing failures
* Webhook event queue for manual processing
    """,
    'depends': ['payment_stripe'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_transaction_views.xml',
        'data/ir_cron_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

