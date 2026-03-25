from odoo import api, fields, models


class AppointmentService(models.Model):
    _name = "website.appointment.service"
    _description = "Website Appointment Service"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    description = fields.Html()
    active = fields.Boolean(default=True)
    duration_minutes = fields.Integer(string="Duration (min)", default=30)
    price = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id.id,
    )
    provider_ids = fields.One2many(
        "website.appointment.provider",
        "service_id",
        string="Providers",
    )
    website_published = fields.Boolean(default=True)


