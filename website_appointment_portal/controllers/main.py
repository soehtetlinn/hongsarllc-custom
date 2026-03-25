from odoo import http
from odoo.http import request
from datetime import datetime, timedelta


class WebsiteAppointment(http.Controller):
    @http.route(['/appointments', '/appointments/page/<int:page>'], type='http', auth='public', website=True)
    def appointments_list(self, page=1, **kw):
        domain = [('website_published', '=', True), ('active', '=', True)]
        services = request.env['website.appointment.service'].sudo().search(domain)
        return request.render('website_appointment_portal.website_appointment_services', {
            'services': services,
        })

    @http.route(['/appointments/<int:service_id>'], type='http', auth='public', website=True)
    def appointment_detail(self, service_id, **kw):
        service = request.env['website.appointment.service'].sudo().browse(service_id)
        if not service or not service.website_published:
            return request.not_found()
        providers = request.env['website.appointment.provider'].sudo().search([('service_id', '=', service.id), ('active', '=', True)])
        return request.render('website_appointment_portal.website_appointment_service_detail', {
            'service': service,
            'providers': providers,
        })

    @http.route(['/appointments/<int:service_id>/slots'], type='json', auth='public', website=True)
    def appointment_slots(self, service_id, provider_id=None, date_from=None, date_to=None, **kw):
        service = request.env['website.appointment.service'].sudo().browse(service_id)
        provider = request.env['website.appointment.provider'].sudo().browse(int(provider_id)) if provider_id else None
        if not provider:
            provider = request.env['website.appointment.provider'].sudo().search([('service_id', '=', service.id)], limit=1)
        date_from = datetime.fromisoformat(date_from) if date_from else datetime.utcnow()
        date_to = datetime.fromisoformat(date_to) if date_to else (date_from + timedelta(days=7))
        slots = provider._generate_slots(date_from, date_to)

        # Exclude full slots and compute remaining capacity
        result = []
        Booking = request.env['calendar.event'].sudo()
        for start in slots:
            end = start + timedelta(minutes=service.duration_minutes or 30)
            overlapping = Booking.search_count([
                ('provider_id', '=', provider.id),
                ('state', '!=', 'cancelled'),
                ('start', '<', end),
                ('stop', '>', start),
            ])
            capacity = provider.slot_capacity or 1
            remaining = max(capacity - overlapping, 0)
            if remaining > 0:
                result.append({
                    'start': start.isoformat(),
                    'end': end.isoformat(),
                    'capacity': capacity,
                    'booked': overlapping,
                    'available': remaining,
                })
        return result

    @http.route(['/appointments/<int:service_id>/book'], type='http', auth='user', website=True, methods=['POST'], csrf=False)
    def appointment_book(self, service_id, provider_id, slot_start, **kw):
        partner = request.env.user.partner_id
        service = request.env['website.appointment.service'].sudo().browse(service_id)
        provider = request.env['website.appointment.provider'].sudo().browse(int(provider_id))
        start_dt = datetime.fromisoformat(slot_start)
        end_dt = start_dt + timedelta(minutes=service.duration_minutes or 30)
        booking = request.env['website.appointment.booking'].sudo().create({
            'service_id': service.id,
            'provider_id': provider.id,
            'partner_id': partner.id,
            'datetime_start': start_dt,
        })
        booking.action_confirm()
        return request.redirect('/my/appointments')


