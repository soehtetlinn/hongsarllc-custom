# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class StripeWebhookLog(models.Model):
    """Model to log and track Stripe webhook events for monitoring and retry processing."""
    
    _name = 'stripe.webhook.log'
    _description = 'Stripe Webhook Event Log'
    _order = 'received_at desc'
    _rec_name = 'event_id'

    event_id = fields.Char(
        string='Event ID',
        required=True,
        index=True,
        help='Stripe event ID'
    )
    event_type = fields.Char(
        string='Event Type',
        required=True,
        index=True,
        help='Stripe event type (e.g., payment_intent.succeeded)'
    )
    status = fields.Selection([
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('validation_error', 'Validation Error'),
        ('security_error', 'Security Error'),
        ('data_error', 'Data Error'),
        ('error', 'Error'),
        ('failed', 'Failed'),
        ('queued_for_retry', 'Queued for Retry'),
        ('ignored', 'Ignored'),
        ('catastrophic_error', 'Catastrophic Error'),
        ('parsing_error', 'Parsing Error'),
    ], string='Status', required=True, default='processing', index=True)
    
    received_at = fields.Datetime(
        string='Received At',
        required=True,
        default=fields.Datetime.now,
        index=True
    )
    processed_at = fields.Datetime(string='Processed At')
    
    raw_payload = fields.Text(string='Raw Payload', help='Raw webhook event payload (truncated)')
    error_type = fields.Char(string='Error Type')
    error_message = fields.Text(string='Error Message')
    error_traceback = fields.Text(string='Error Traceback')
    notes = fields.Text(string='Notes')
    
    retry_count = fields.Integer(
        string='Retry Count',
        default=0,
        help='Number of retry attempts'
    )
    next_retry_at = fields.Datetime(
        string='Next Retry At',
        index=True,
        help='Scheduled time for next retry attempt'
    )
    last_error = fields.Text(string='Last Error')
    
    transaction_id = fields.Many2one(
        'payment.transaction',
        string='Transaction',
        ondelete='set null',
        help='Related payment transaction if found'
    )
    
    # Computed fields for better UI
    is_failed = fields.Boolean(
        string='Is Failed',
        compute='_compute_is_failed',
        store=True
    )
    can_retry = fields.Boolean(
        string='Can Retry',
        compute='_compute_can_retry'
    )
    
    @api.depends('status')
    def _compute_is_failed(self):
        """Mark as failed if status indicates failure."""
        for record in self:
            record.is_failed = record.status in (
                'error', 'failed', 'data_error', 'catastrophic_error'
            )
    
    def _compute_can_retry(self):
        """Determine if the webhook can be retried."""
        for record in self:
            record.can_retry = (
                record.status in ('error', 'data_error', 'queued_for_retry') and
                record.retry_count < 3 and
                (not record.next_retry_at or record.next_retry_at <= fields.Datetime.now())
            )
    
    def action_retry(self):
        """Manually retry processing a failed webhook event."""
        self.ensure_one()
        
        if not self.can_retry:
            raise UserError(_('This webhook cannot be retried at this time.'))
        
        try:
            # Parse the raw payload
            event = json.loads(self.raw_payload) if self.raw_payload else {}
            
            # Create a mock request context for processing
            # Note: This is a simplified retry - in production you might want to
            # use a more sophisticated approach
            self.env['payment.transaction'].sudo()._process_stripe_webhook_event(
                event, webhook_log=self
            )
            
            self.write({
                'status': 'processed',
                'processed_at': fields.Datetime.now(),
                'retry_count': self.retry_count + 1,
            })
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Webhook event has been successfully reprocessed.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            self.write({
                'status': 'error',
                'last_error': str(e)[:500],
                'retry_count': self.retry_count + 1,
            })
            raise UserError(_('Failed to retry webhook: %s', str(e)))
    
    @api.model
    def _retry_queued_webhooks(self):
        """Cron job to automatically retry queued webhook events."""
        queued_webhooks = self.search([
            ('status', '=', 'queued_for_retry'),
            ('next_retry_at', '<=', fields.Datetime.now()),
            ('retry_count', '<', 3),
        ])
        
        _logger.info("Processing %s queued webhook events for retry", len(queued_webhooks))
        
        for webhook_log in queued_webhooks:
            try:
                # This is a placeholder - actual implementation would process the webhook
                # For now, we'll just log it
                _logger.info("Retrying webhook event: %s (attempt %s)", 
                            webhook_log.event_id, webhook_log.retry_count + 1)
                # In a full implementation, you would call the webhook processing logic here
                # webhook_log.action_retry()
            except Exception as e:
                _logger.error("Failed to retry webhook %s: %s", webhook_log.event_id, str(e))
                webhook_log.write({
                    'last_error': str(e)[:500],
                    'retry_count': webhook_log.retry_count + 1,
                })

