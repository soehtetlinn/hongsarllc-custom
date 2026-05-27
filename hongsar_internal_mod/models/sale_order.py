# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models
from odoo.osv import expression


class SaleOrder(models.Model):
    _inherit = "sale.order"

    own_date = fields.Boolean(
        string="Own Date",
        copy=False,
        help="If enabled, confirming the quotation keeps the current order date "
        "instead of setting it to the confirmation date.",
    )

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
