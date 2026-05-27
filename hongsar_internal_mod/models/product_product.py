# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, models

HONGSAR_INTERNAL_REF_ORDER = "default_code, name, id"


class ProductProduct(models.Model):
    _inherit = "product.product"

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
        """Sort dropdown/search results by internal reference, then name."""
        ids = [row[0] for row in results]
        labels = dict(results)
        products = self.browse(ids).sorted(
            key=lambda product: (
                (product.default_code or "\uffff").upper(),
                (product.name or "").upper(),
                product.id,
            )
        )
        return [(product.id, labels[product.id]) for product in products]
