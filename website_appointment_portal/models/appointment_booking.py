from odoo import api, fields, models, exceptions, _
from datetime import datetime, timedelta


class AppointmentBooking(models.Model):
    _name = "website.appointment.booking"
    _description = "Appointment Booking"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(readonly=True, copy=False)
    service_id = fields.Many2one("website.appointment.service", required=True)
    provider_id = fields.Many2one("website.appointment.provider", required=True)
    partner_id = fields.Many2one("res.partner", required=True)
    datetime_start = fields.Datetime(required=True)
    datetime_end = fields.Datetime(compute="_compute_end", store=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True)

    @api.depends("datetime_start", "service_id.duration_minutes")
    def _compute_end(self):
        for rec in self:
            if rec.datetime_start and rec.service_id:
                rec.datetime_end = rec.datetime_start + timedelta(minutes=rec.service_id.duration_minutes or 30)
            else:
                rec.datetime_end = rec.datetime_start

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("name"):
                vals["name"] = self.env["ir.sequence"].next_by_code("website.appointment.booking") or _("New")
        records = super().create(vals_list)
        for rec in records:
            rec._check_capacity()
        return records

    def _check_capacity(self):
        for rec in self:
            overlapping = self.search_count([
                ("provider_id", "=", rec.provider_id.id),
                ("state", "!=", "cancelled"),
                ("datetime_start", "<", rec.datetime_end),
                ("datetime_end", ">", rec.datetime_start),
            ])
            if overlapping > (rec.provider_id.slot_capacity or 1):
                raise exceptions.ValidationError(_("Selected slot is full. Please choose another time."))

    def action_confirm(self):
        self.write({"state": "confirmed"})
        return True

    def action_cancel(self):
        self.write({"state": "cancelled"})
        return True


