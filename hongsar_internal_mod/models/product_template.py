from odoo import api, fields, models

from .product_product import HONGSAR_INTERNAL_REF_ORDER


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_other_name = fields.Char(string="Product (Other Name)")

    @api.model
    def _hongsar_get_internal_ref_order(self, order):
        if self.env.context.get("hongsar_order_by_internal_ref") and not order:
            return HONGSAR_INTERNAL_REF_ORDER
        return order

    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        return super().search(
            domain,
            offset=offset,
            limit=limit,
            order=self._hongsar_get_internal_ref_order(order),
        )

    @api.model
    def search_fetch(self, domain, field_names, offset=0, limit=None, order=None):
        return super().search_fetch(
            domain,
            field_names,
            offset=offset,
            limit=limit,
            order=self._hongsar_get_internal_ref_order(order),
        )

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        results = super().name_search(name, args, operator, limit)
        if not self.env.context.get("hongsar_order_by_internal_ref") or not results:
            return results
        return self._hongsar_sort_name_search_results(results)

    @api.model
    def _hongsar_sort_name_search_results(self, results):
        ids = [row[0] for row in results]
        labels = dict(results)
        templates = self.browse(ids).sorted(
            key=lambda template: (
                (template.default_code or "\uffff").upper(),
                (template.name or "").upper(),
                template.id,
            )
        )
        return [(template.id, labels[template.id]) for template in templates]
