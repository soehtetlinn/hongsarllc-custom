# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
except ImportError:
    _logger.warning("SendGrid library not installed")
    SendGridAPIClient = None


class MailMail(models.Model):
    _inherit = 'mail.mail'

    def _send_prepare_values(self, partner=None):
        """Prepare email values"""
        res = super(MailMail, self)._send_prepare_values(partner=partner)
        return res

    def _send(self, auto_commit=False, raise_exception=False, smtp_session=None):
        """Override send to use SendGrid API if configured"""
        IrMailServer = self.env['ir.mail_server']
        
        # Check if SendGrid is configured
        mail_server = IrMailServer.sudo().search([('smtp_authentication', '=', 'sendgrid')], limit=1)
        
        if mail_server:
            # Use SendGrid API
            for mail_id in self.ids:
                mail = self.browse(mail_id)
                try:
                    self._send_via_sendgrid(mail, mail_server)
                    mail.write({
                        'state': 'sent',
                        'failure_reason': False,
                    })
                    _logger.info('Mail %s sent via SendGrid', mail.id)
                except Exception as e:
                    _logger.error('Failed to send mail %s via SendGrid: %s', mail.id, str(e))
                    mail.write({
                        'state': 'exception',
                        'failure_reason': str(e),
                    })
                    if raise_exception:
                        raise
                if auto_commit:
                    self.env.cr.commit()
            return True
        else:
            # Use standard SMTP
            return super(MailMail, self)._send(
                auto_commit=auto_commit,
                raise_exception=raise_exception,
                smtp_session=smtp_session
            )

    def _send_via_sendgrid(self, mail, mail_server):
        """Send email via SendGrid API"""
        if not SendGridAPIClient:
            raise UserError(_("SendGrid library not installed. Run: pip3 install sendgrid"))
        
        api_key = mail_server.sendgrid_api_key or mail_server._get_sendgrid_api_key()
        if not api_key:
            raise UserError(_("SendGrid API Key not configured"))
        
        # Prepare email data
        from_email = mail.email_from or mail_server.smtp_user or 'noreply@example.com'
        to_emails = []
        
        if mail.email_to:
            to_emails.extend(mail.email_to.split(','))
        if mail.recipient_ids:
            to_emails.extend(mail.recipient_ids.mapped('email'))
        
        if not to_emails:
            raise UserError(_("No recipient specified"))
        
        # Clean email addresses
        to_emails = [email.strip() for email in to_emails if email.strip()]
        
        # Create SendGrid message
        message = Mail(
            from_email=from_email,
            to_emails=to_emails,
            subject=mail.subject or 'No Subject',
        )
        
        # Set body (prefer HTML)
        if mail.body_html:
            message.content = Content("text/html", mail.body_html)
        else:
            message.content = Content("text/plain", mail.body or '')
        
        # Add CC if any
        if mail.email_cc:
            cc_emails = [email.strip() for email in mail.email_cc.split(',') if email.strip()]
            for cc_email in cc_emails:
                message.add_cc(cc_email)
        
        # Send via SendGrid
        try:
            sg = SendGridAPIClient(api_key)
            response = sg.send(message)
            
            if response.status_code not in [200, 202]:
                raise UserError(_("SendGrid returned status: %s") % response.status_code)
            
            _logger.info('SendGrid API response: %s', response.status_code)
            return True
            
        except Exception as e:
            _logger.error('SendGrid API error: %s', str(e))
            raise UserError(_("Failed to send email via SendGrid: %s") % str(e))

