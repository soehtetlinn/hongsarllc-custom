from odoo import http
from odoo.http import request

import logging

_logger = logging.getLogger(__name__)

class PortalAppointments(http.Controller):
    @http.route(['/my/custom-appointments'], type='http', auth='user', website=True)
    def portal_my_appointments(self, **kw):
        _logger.info(f"Portal my appointments (custom): {kw}")
        bookings = request.env['calendar.event'].sudo().search([
            # ('partner_id', '=', request.env.user.partner_id.id),
            # ('state', '!=', 'cancelled'),
        ], order='start desc')
        return request.render('website_appointment_portal.portal_my_appointments', {
            'bookings': bookings,
        })


