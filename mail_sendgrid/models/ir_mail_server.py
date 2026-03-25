# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
except ImportError:
    _logger.warning("SendGrid library not installed. Run: pip3 install sendgrid")
    SendGridAPIClient = None


class IrMailServer(models.Model):
    _inherit = 'ir.mail_server'

    smtp_authentication = fields.Selection(
        selection_add=[('sendgrid', 'SendGrid API')],
        ondelete={'sendgrid': 'set default'}
    )
    sendgrid_api_key = fields.Char(
        string='SendGrid API Key',
        help='Your SendGrid API Key (starts with SG.)'
    )

    @api.model
    def _get_sendgrid_api_key(self):
        """Get SendGrid API key from system parameters or mail server"""
        # Try to get from mail server
        mail_server = self.sudo().search([('smtp_authentication', '=', 'sendgrid')], limit=1)
        if mail_server and mail_server.sendgrid_api_key:
            return mail_server.sendgrid_api_key
        
        # Fallback to system parameter
        api_key = self.env['ir.config_parameter'].sudo().get_param('sendgrid.api_key')
        return api_key

    def test_smtp_connection(self):
        """Test SendGrid connection"""
        self.ensure_one()
        if self.smtp_authentication == 'sendgrid':
            if not SendGridAPIClient:
                raise UserError(_("SendGrid library not installed. Run: pip3 install sendgrid"))
            
            api_key = self.sendgrid_api_key or self._get_sendgrid_api_key()
            if not api_key:
                raise UserError(_("Please configure SendGrid API Key"))
            
            try:
                sg = SendGridAPIClient(api_key)
                # Test by checking API key validity
                response = sg.client.scopes.get()
                if response.status_code == 200:
                    raise UserError(_("SendGrid connection successful! ✅\n\nYour API key is valid and ready to send emails."))
                else:
                    raise UserError(_("SendGrid connection failed. Status: %s") % response.status_code)
            except Exception as e:
                raise UserError(_("SendGrid connection failed: %s") % str(e))
        else:
            return super(IrMailServer, self).test_smtp_connection()

