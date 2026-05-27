# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models
from odoo.osv import expression


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

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
