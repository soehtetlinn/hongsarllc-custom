# -*- coding: utf-8 -*-
{
    'name': 'Product Course Link',
    'version': '18.1',
    'category': 'Product',
    'summary': 'Auto-create course when product is created and link them',
    'description': """
Product Course Link
==================

This module automatically creates a course when a product is created:
* When a user creates a product, a course is automatically created with the same name
* One2many relationship between product and course
* New "Courses" notebook page in product form view (besides Accounting page)
* View and manage courses linked to products

Features:
---------
* Auto-creation of course on product creation
* One2many relationship: product → courses
* Form view extension with new notebook page
* Course management directly from product form

Author: Soe Htet Linn
    """,
    'author': 'Soe Htet Linn',
    'depends': ['product', 'website_slides'],
    'data': [
        'views/product_template_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

