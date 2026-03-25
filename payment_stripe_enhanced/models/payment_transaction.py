# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    """Extend payment.transaction to add webhook retry processing support."""
    
    _inherit = 'payment.transaction'
    
    stripe_webhook_log_ids = fields.One2many(
        'stripe.webhook.log',
        'transaction_id',
        string='Webhook Logs'
    )
    
    def _process_stripe_webhook_event(self, event, webhook_log=None):
        """Process a Stripe webhook event (used for retry mechanism).
        
        This is a helper method that can be called manually to retry processing
        a webhook event from the webhook log.
        """
        # This would need to integrate with the existing webhook processing logic
        # For now, it's a placeholder that can be extended
        _logger.info("Processing Stripe webhook event for retry: %s", event.get('id'))
        # Actual implementation would call the appropriate webhook processing methods
        # This is a simplified version
        return True

