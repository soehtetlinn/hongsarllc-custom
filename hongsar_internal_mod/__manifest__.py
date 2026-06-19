# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html)

{
    "name": "Hongsar Internal Mod",
    "summary": "Product visibility by company, internal ref search order, Own Date on SO confirm.",
    "version": "18.0.1.1.0",
    "category": "Sales/Purchase",
    "author": "Custom",
    "license": "LGPL-3",
    "depends": ["product", "sale", "purchase"],
    "data": [
        "views/product_template_views.xml",
        "views/res_config_settings_views.xml",
        "views/sale_order_views.xml",
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    "application": False,
}
