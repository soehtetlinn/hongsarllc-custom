# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = "sale.order"

    own_date = fields.Boolean(
        string="Own Date",
        copy=False,
        help="If enabled, confirming the quotation keeps the current order date "
        "instead of setting it to the confirmation date.",
    )
    is_charged_stripe_fees = fields.Boolean(
        string="Charge Stripe Fees",
        copy=False,
        help="When enabled, Stripe service charge lines are added using the "
        "percentage and fixed fee configured in Sales settings.",
    )

    STRIPE_CHARGE_NAME_BASE = "Service Charges for Stripe (Base Fees)"
    STRIPE_CHARGE_NAME_AMT = "Service Charges for Stripe (Amt)"
    STRIPE_PRODUCT_NAME_BASE = "Stripe Service Charge( Base Fees )"
    STRIPE_PRODUCT_NAME_AMT = "Stripe Service Charge( Amount )"

    def _prepare_confirmation_values(self):
        """Keep quotation date_order when Own Date is set on all orders."""
        values = {"state": "sale"}
        if not all(self.mapped("own_date")):
            values["date_order"] = fields.Datetime.now()
        return values

    def action_confirm(self):
        """Confirm per order when Own Date is mixed in a multi-record batch."""
        if self.filtered("own_date") and self.filtered(lambda o: not o.own_date):
            for order in self:
                super(SaleOrder, order).action_confirm()
            return True
        return super().action_confirm()

    def _get_product_catalog_domain(self):
        domain = super()._get_product_catalog_domain()
        field_name = "x_studio_visible_company"
        if field_name not in self.env["product.template"]._fields:
            return domain
        company = self.company_id
        if not company:
            return domain
        visible = [
            "|",
            ("product_tmpl_id.%s" % field_name, "=", False),
            ("product_tmpl_id.%s" % field_name, "=", company.id),
        ]
        return expression.AND([domain, visible])

    def _get_stripe_charge_product_ids(self):
        self.ensure_one()
        company = self.company_id
        return {
            company.stripe_service_charge_base_product_id,
            company.stripe_service_charge_amt_product_id,
        } - {False}

    def _is_stripe_service_charge_line(self, line):
        if line.product_id in self._get_stripe_charge_product_ids():
            return True
        return bool(line.is_stripe_service_charge)

    def _get_stripe_service_charge_product(self, fee_type):
        self.ensure_one()
        field_name = (
            "stripe_service_charge_base_product_id"
            if fee_type == "base_fees"
            else "stripe_service_charge_amt_product_id"
        )
        product = self.company_id[field_name]
        if product:
            return product
        product_name = (
            self.STRIPE_PRODUCT_NAME_BASE
            if fee_type == "base_fees"
            else self.STRIPE_PRODUCT_NAME_AMT
        )
        product = self.env["product.product"].sudo().create(
            {
                "name": product_name,
                "type": "service",
                "invoice_policy": "order",
                "list_price": 0.0,
                "company_id": self.company_id.id,
            }
        )
        self.company_id.sudo()[field_name] = product
        return product

    def _get_stripe_service_charge_lines(self, fee_type=None):
        self.ensure_one()
        lines = self.order_line.filtered(
            lambda line: not line.display_type
            and self._is_stripe_service_charge_line(line)
        )
        if not fee_type:
            return lines
        product = self._get_stripe_service_charge_product(fee_type)
        return lines.filtered(lambda line: line.product_id == product)

    def _get_stripe_service_charge_base(self):
        self.ensure_one()
        lines = self.order_line.filtered(
            lambda line: not line.display_type
            and not self._is_stripe_service_charge_line(line)
            and not line.is_downpayment
        )
        return sum(lines.mapped("price_subtotal"))

    def _prepare_stripe_service_charge_line_vals(self, amount, fee_type, name):
        self.ensure_one()
        product = self._get_stripe_service_charge_product(fee_type)
        taxes = product.taxes_id._filter_taxes_by_company(self.company_id)
        if self.partner_id and self.fiscal_position_id:
            taxes = self.fiscal_position_id.map_tax(taxes)
        values = {
            "name": name,
            "price_unit": amount,
            "product_uom_qty": 1,
            "product_uom": product.uom_id.id,
            "product_id": product.id,
            "tax_id": [(6, 0, taxes.ids)],
            "is_stripe_service_charge": True,
            "stripe_charge_fee_type": fee_type,
        }
        if self.order_line:
            values["sequence"] = self.order_line[-1].sequence + 1
        return values

    def _create_stripe_service_charge_line(self, amount, fee_type, name):
        self.ensure_one()
        values = self._prepare_stripe_service_charge_line_vals(amount, fee_type, name)
        values["order_id"] = self.id
        return self.env["sale.order.line"].with_context(
            hongsar_stripe_charge_update=True
        ).sudo().create(values)

    def _remove_stripe_service_charge_line(self, fee_type=None):
        self.ensure_one()
        charge_lines = self._get_stripe_service_charge_lines(fee_type)
        if not charge_lines:
            return
        if isinstance(self.id, int):
            to_delete = charge_lines.filtered(lambda line: line.qty_invoiced == 0)
            if charge_lines != to_delete:
                raise UserError(
                    _(
                        "You cannot remove the Stripe service charge on an order "
                        "where it was already invoiced."
                    )
                )
            to_delete.with_context(hongsar_stripe_charge_update=True).unlink()
        else:
            self.order_line = self.order_line.filtered(
                lambda line: line not in charge_lines
            )

    def _get_stripe_charge_specs(self):
        self.ensure_one()
        if not self.is_charged_stripe_fees:
            return []
        percent = self.company_id.stripe_service_charge_percent or 0.0
        fixed = self.company_id.stripe_service_charge_fixed_amount or 0.0
        if percent <= 0 and fixed <= 0:
            return []
        specs = []
        base = self._get_stripe_service_charge_base()
        if percent > 0:
            amount = self.currency_id.round(base * (percent / 100.0))
            if amount:
                specs.append(
                    {
                        "fee_type": "base_fees",
                        "amount": amount,
                        "name": self.STRIPE_CHARGE_NAME_BASE,
                    }
                )
        if fixed > 0:
            specs.append(
                {
                    "fee_type": "amt",
                    "amount": self.currency_id.round(fixed),
                    "name": self.STRIPE_CHARGE_NAME_AMT,
                }
            )
        return specs

    def _sync_stripe_service_charge(self, persist=False):
        if self.env.context.get("hongsar_stripe_charge_update"):
            return
        for order in self.with_context(hongsar_stripe_charge_update=True):
            specs = order._get_stripe_charge_specs()
            if persist and isinstance(order.id, int):
                order._remove_stripe_service_charge_line()
                for spec in specs:
                    order._create_stripe_service_charge_line(
                        spec["amount"], spec["fee_type"], spec["name"]
                    )
                continue
            regular_lines = order.order_line.filtered(
                lambda line: not order._is_stripe_service_charge_line(line)
            )
            charge_lines = order.env["sale.order.line"]
            for spec in specs:
                vals = order._prepare_stripe_service_charge_line_vals(
                    spec["amount"], spec["fee_type"], spec["name"]
                )
                charge_lines |= order.env["sale.order.line"].new(vals)
            order.order_line = regular_lines | charge_lines

    @api.onchange("is_charged_stripe_fees", "order_line")
    def _onchange_stripe_service_charge(self):
        self._sync_stripe_service_charge(persist=False)

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        orders.filtered("is_charged_stripe_fees")._sync_stripe_service_charge(
            persist=True
        )
        return orders

    def write(self, vals):
        res = super().write(vals)
        if {"is_charged_stripe_fees", "order_line"} & set(vals.keys()):
            self._sync_stripe_service_charge(persist=True)
        return res

    def _get_update_prices_lines(self):
        lines = super()._get_update_prices_lines()
        return lines.filtered(
            lambda line: not line.is_stripe_service_charge
            and not line._is_stripe_service_charge_line()
        )
