# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    stripe_service_charge_percent = fields.Float(
        string="Stripe Service Charge %",
        default=2.9,
        help="Percentage applied to the untaxed order subtotal when "
        "'Charge Stripe Fees' is enabled on a sales order (e.g. 2.9 for 2.9%).",
    )
    stripe_service_charge_fixed_amount = fields.Monetary(
        string="Stripe Fixed Fee",
        currency_field="currency_id",
        default=0.0,
        help="Fixed amount added as a separate service charge line when "
        "'Charge Stripe Fees' is enabled (e.g. 0.30 for Stripe's per-transaction fee).",
    )
    stripe_service_charge_base_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Stripe Service Charge (Base Fees) Product",
        domain=[
            ("type", "=", "service"),
            ("invoice_policy", "=", "order"),
        ],
        check_company=True,
        help="Product used for the percentage-based Stripe service charge line.",
    )
    stripe_service_charge_amt_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Stripe Service Charge (Amount) Product",
        domain=[
            ("type", "=", "service"),
            ("invoice_policy", "=", "order"),
        ],
        check_company=True,
        help="Product used for the fixed-amount Stripe service charge line.",
    )
