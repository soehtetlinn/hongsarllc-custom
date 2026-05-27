# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_id = fields.Many2one(
        context={"hongsar_order_by_internal_ref": True},
        domain="["
        "('sale_ok', '=', True), "
        "'|', "
        "('product_tmpl_id.x_studio_visible_company', '=', False), "
        "('product_tmpl_id.x_studio_visible_company', '=', company_id)"
        "]",
    )
    product_template_id = fields.Many2one(
        context={"hongsar_order_by_internal_ref": True},
        domain="["
        "('sale_ok', '=', True), "
        "'|', "
        "('x_studio_visible_company', '=', False), "
        "('x_studio_visible_company', '=', company_id)"
        "]",
    )

    @api.constrains("product_id", "company_id", "display_type")
    def _check_product_visible_company_sale(self):
        field_name = "x_studio_visible_company"
        for line in self:
            if line.display_type or not line.product_id or not line.company_id:
                continue
            tmpl = line.product_id.product_tmpl_id
            if field_name not in tmpl._fields:
                continue
            vis = tmpl[field_name]
            if vis and vis != line.company_id:
                raise ValidationError(
                    _(
                        "Product “%(product)s” is restricted to company “%(allowed)s” "
                        "and cannot be used on this order (company “%(current)s”).",
                        product=line.product_id.display_name,
                        allowed=vis.display_name,
                        current=line.company_id.display_name,
                    )
                )
