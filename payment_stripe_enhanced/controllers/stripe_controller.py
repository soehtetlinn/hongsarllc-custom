# -*- coding: utf-8 -*-

import json
import logging
import traceback
from datetime import datetime, timedelta

from werkzeug.exceptions import Forbidden, BadRequest

from odoo import http, _
from odoo.exceptions import ValidationError, UserError
from odoo.http import request

from odoo.addons.payment_stripe.controllers.main import StripeController
from odoo.addons.payment_stripe.const import HANDLED_WEBHOOK_EVENTS

_logger = logging.getLogger(__name__)


class StripeControllerEnhanced(StripeController):
    """Enhanced Stripe controller with comprehensive error handling and fallback mechanisms."""

    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY_HOURS = 1

    @http.route('/payment/stripe/webhook', type='http', methods=['POST'], auth='public', csrf=False)
    def stripe_webhook(self):
        """Enhanced webhook handler with comprehensive error handling and fallback mechanisms.
        
        This method extends the base webhook handler with:
        - Comprehensive exception handling for all error types
        - Retry mechanism for transient failures
        - Detailed logging for debugging
        - Fallback queue for failed webhooks
        - Proper HTTP status code responses
        """
        event_id = None
        event_type = None
        webhook_log_id = None
        
        try:
            # Get and parse the webhook event
            try:
                event = request.get_json_data()
                event_id = event.get('id')
                event_type = event.get('type', 'unknown')
                _logger.info(
                    "Stripe webhook received: event_id=%s, event_type=%s",
                    event_id, event_type
                )
            except (ValueError, TypeError, KeyError) as e:
                _logger.error(
                    "Failed to parse webhook event: %s\nPayload: %s",
                    str(e), request.httprequest.data.decode('utf-8')[:500]
                )
                # Log the failed webhook for manual review
                self._log_webhook_failure(
                    event_id=None,
                    event_type=None,
                    error_type=type(e).__name__,
                    error_message=f"Failed to parse webhook event: {str(e)}",
                    raw_payload=request.httprequest.data.decode('utf-8')[:1000],
                    status='parsing_error'
                )
                # Return 400 Bad Request - Stripe will retry, but we've logged it
                return request.make_json_response({'error': 'Invalid webhook payload'}, status=400)
            
            # Create webhook log entry
            webhook_log = request.env['stripe.webhook.log'].sudo().create({
                'event_id': event_id,
                'event_type': event_type,
                'status': 'processing',
                'raw_payload': json.dumps(event)[:5000],  # Limit size
                'received_at': datetime.utcnow(),
            })
            webhook_log_id = webhook_log.id
            
            # Check if this is a handled event type
            if event_type not in HANDLED_WEBHOOK_EVENTS:
                _logger.info("Ignoring unhandled webhook event type: %s", event_type)
                webhook_log.write({
                    'status': 'ignored',
                    'notes': f'Event type {event_type} is not in HANDLED_WEBHOOK_EVENTS'
                })
                # Acknowledge the webhook even if we don't handle it
                return request.make_json_response('')
            
            try:
                # Call the parent webhook handler
                # Wrap in try/except to catch any exceptions that might be raised
                try:
                    result = super().stripe_webhook()
                except Exception as parent_error:
                    # If parent raises an exception, log it but check if it's a ValidationError
                    # that might be expected (e.g., duplicate processing)
                    if isinstance(parent_error, ValidationError):
                        # Re-raise ValidationError to be handled by outer ValidationError handler
                        raise
                    # For other exceptions, log and re-raise
                    _logger.warning(
                        "Parent webhook handler raised exception for event %s: %s",
                        event_id, str(parent_error)
                    )
                    raise
                
                # If successful, mark the log as processed
                webhook_log.write({
                    'status': 'processed',
                    'processed_at': datetime.utcnow(),
                })
                _logger.info("Successfully processed webhook event: %s", event_id)
                
                return result
                
            except ValidationError as ve:
                # Validation errors are expected in some cases (e.g., duplicate processing)
                error_msg = str(ve)
                _logger.warning(
                    "Validation error processing webhook event %s: %s",
                    event_id, error_msg
                )
                
                webhook_log.write({
                    'status': 'validation_error',
                    'error_type': 'ValidationError',
                    'error_message': error_msg[:500],
                    'notes': 'Transaction validation failed - may have been processed already'
                })
                
                # Acknowledge to avoid retries for validation errors
                return request.make_json_response('')
                
            except Forbidden as fe:
                # Signature verification failed or timestamp too old
                error_msg = str(fe)
                _logger.error(
                    "Security error processing webhook event %s: %s",
                    event_id, error_msg
                )
                
                webhook_log.write({
                    'status': 'security_error',
                    'error_type': 'Forbidden',
                    'error_message': error_msg[:500],
                    'notes': 'Signature verification failed or timestamp invalid'
                })
                
                # Return 403 - Stripe may retry, but this is a security issue
                return request.make_json_response({'error': 'Forbidden'}, status=403)
                
            except (KeyError, AttributeError, TypeError) as e:
                # Missing required data in webhook payload
                error_msg = f"{type(e).__name__}: {str(e)}"
                error_trace = traceback.format_exc()
                _logger.error(
                    "Data error processing webhook event %s: %s\n%s",
                    event_id, error_msg, error_trace
                )
                
                webhook_log.write({
                    'status': 'data_error',
                    'error_type': type(e).__name__,
                    'error_message': error_msg[:500],
                    'error_traceback': error_trace[:2000],
                    'notes': 'Missing or invalid data in webhook payload'
                })
                
                # Queue for retry - this might be a transient issue
                self._queue_webhook_for_retry(webhook_log_id, event, error_msg)
                
                # Return 500 to trigger Stripe retry
                return request.make_json_response({'error': 'Internal server error'}, status=500)
                
            except Exception as e:
                # Unexpected error - log it and queue for retry
                error_msg = f"{type(e).__name__}: {str(e)}"
                error_trace = traceback.format_exc()
                _logger.error(
                    "Unexpected error processing webhook event %s: %s\n%s",
                    event_id, error_msg, error_trace
                )
                
                webhook_log.write({
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': error_msg[:500],
                    'error_traceback': error_trace[:2000],
                    'notes': 'Unexpected error during webhook processing'
                })
                
                # Queue for retry if retries haven't been exhausted
                if webhook_log.retry_count < self.MAX_RETRY_ATTEMPTS:
                    self._queue_webhook_for_retry(webhook_log_id, event, error_msg)
                    # Return 500 to trigger Stripe retry
                    return request.make_json_response({'error': 'Internal server error'}, status=500)
                else:
                    # Max retries exceeded - acknowledge but log for manual processing
                    webhook_log.write({
                        'status': 'failed',
                        'notes': f'Max retry attempts ({self.MAX_RETRY_ATTEMPTS}) exceeded'
                    })
                    _logger.error(
                        "Max retries exceeded for webhook event %s. Manual intervention required.",
                        event_id
                    )
                    # Acknowledge to stop Stripe from retrying
                    return request.make_json_response('')
                    
        except Exception as e:
            # Catastrophic error - something went very wrong
            error_msg = f"{type(e).__name__}: {str(e)}"
            error_trace = traceback.format_exc()
            _logger.critical(
                "Catastrophic error in webhook handler: %s\n%s",
                error_msg, error_trace
            )
            
            # Try to log the failure if we have event info
            if event_id:
                self._log_webhook_failure(
                    event_id=event_id,
                    event_type=event_type,
                    error_type=type(e).__name__,
                    error_message=error_msg[:500],
                    error_traceback=error_trace[:2000],
                    raw_payload=json.dumps(event)[:1000] if 'event' in locals() else None,
                    status='catastrophic_error'
                )
            
            # Return 500 - let Stripe retry
            return request.make_json_response({'error': 'Internal server error'}, status=500)

    def _log_webhook_failure(self, event_id=None, event_type=None, error_type=None,
                            error_message=None, error_traceback=None, raw_payload=None, status='error'):
        """Log a webhook processing failure."""
        try:
            request.env['stripe.webhook.log'].sudo().create({
                'event_id': event_id or 'unknown',
                'event_type': event_type or 'unknown',
                'status': status,
                'error_type': error_type,
                'error_message': error_message[:500] if error_message else None,
                'error_traceback': error_traceback[:2000] if error_traceback else None,
                'raw_payload': raw_payload[:5000] if raw_payload else None,
                'received_at': datetime.utcnow(),
            })
        except Exception as log_error:
            _logger.error("Failed to log webhook failure: %s", str(log_error))

    def _queue_webhook_for_retry(self, webhook_log_id, event, error_message):
        """Queue a webhook for retry processing."""
        try:
            webhook_log = request.env['stripe.webhook.log'].sudo().browse(webhook_log_id)
            if webhook_log.exists():
                webhook_log.write({
                    'status': 'queued_for_retry',
                    'retry_count': webhook_log.retry_count + 1,
                    'next_retry_at': datetime.utcnow() + timedelta(hours=self.RETRY_DELAY_HOURS),
                    'last_error': error_message[:500],
                })
                _logger.info(
                    "Queued webhook event %s for retry (attempt %s/%s)",
                    webhook_log.event_id, webhook_log.retry_count, self.MAX_RETRY_ATTEMPTS
                )
        except Exception as retry_error:
            _logger.error("Failed to queue webhook for retry: %s", str(retry_error))

