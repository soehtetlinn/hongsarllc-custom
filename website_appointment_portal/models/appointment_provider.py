from odoo import api, fields, models
from datetime import datetime, timedelta


class AppointmentProvider(models.Model):
    _name = "website.appointment.provider"
    _description = "Appointment Provider"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    service_id = fields.Many2one("website.appointment.service", required=True)
    user_id = fields.Many2one("res.users", string="Responsible User")
    tz = fields.Char(string="Timezone", default=lambda self: self.env.user.tz or "UTC")
    active = fields.Boolean(default=True)

    # Working hours simple config (per day minutes 0-1440 JSON)
    work_start = fields.Float(string="Work Start (hour)", default=9.0)
    work_end = fields.Float(string="Work End (hour)", default=17.0)
    slot_interval_minutes = fields.Integer(default=30)
    slot_capacity = fields.Integer(default=1)

    booking_ids = fields.One2many("website.appointment.booking", "provider_id")

    def _float_hour_to_minutes(self, float_hour):
        return int(round(float_hour * 60))

    def _generate_slots(self, date_from, date_to):
        self.ensure_one()
        slots = []
        start_minutes = self._float_hour_to_minutes(self.work_start)
        end_minutes = self._float_hour_to_minutes(self.work_end)
        interval = max(self.slot_interval_minutes, 5)
        current_day = date_from.date()
        while current_day <= date_to.date():
            day_start = datetime.combine(current_day, datetime.min.time()) + timedelta(minutes=start_minutes)
            day_end = datetime.combine(current_day, datetime.min.time()) + timedelta(minutes=end_minutes)
            start = day_start
            while start + timedelta(minutes=interval) <= day_end:
                slots.append(start)
                start += timedelta(minutes=interval)
            current_day += timedelta(days=1)
        return slots


