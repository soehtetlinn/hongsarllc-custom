# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stripe_service_charge_percent = fields.Float(
        related="company_id.stripe_service_charge_percent",
        readonly=False,
    )
    stripe_service_charge_fixed_amount = fields.Monetary(
        related="company_id.stripe_service_charge_fixed_amount",
        readonly=False,
    )
    stripe_service_charge_base_product_id = fields.Many2one(
        related="company_id.stripe_service_charge_base_product_id",
        readonly=False,
    )
    stripe_service_charge_amt_product_id = fields.Many2one(
        related="company_id.stripe_service_charge_amt_product_id",
        readonly=False,
    )
