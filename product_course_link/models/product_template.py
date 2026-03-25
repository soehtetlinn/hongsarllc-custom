# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Many2many relationship: Get channels linked to product variants of this template
    # Cannot use One2many because slide.channel.product_id points to product.product, not product.template
    channel_ids = fields.Many2many(
        'slide.channel',
        string='Courses',
        compute='_compute_channel_ids',
        store=False,
        readonly=True
    )
    course_count = fields.Integer(
        string='Courses Count',
        compute='_compute_course_count'
    )

    @api.depends('product_variant_ids.channel_ids')
    def _compute_channel_ids(self):
        """Get all channels linked to product variants"""
        for record in self:
            # Get all channels from all product variants
            channels = record.product_variant_ids.mapped('channel_ids')
            record.channel_ids = channels

    @api.depends('channel_ids')
    def _compute_course_count(self):
        for record in self:
            record.course_count = len(record.channel_ids)

    def action_open_courses(self):
        """Open courses linked to this product"""
        self.ensure_one()
        return {
            'name': 'Courses',
            'type': 'ir.actions.act_window',
            'res_model': 'slide.channel',
            'view_mode': 'list,form',
            'domain': [('product_id', 'in', self.product_variant_ids.ids)],
            'context': {
                'default_product_id': self.product_variant_ids[:1].id if self.product_variant_ids else False,
                'search_default_product_id': self.product_variant_ids.ids,
            },
        }

    @api.model_create_multi
    def create(self, vals_list):
        """Auto-create course (slide.channel) when product is created"""
        products = super(ProductTemplate, self).create(vals_list)
        
        # Create slide.channel (course) for each new product
        for product in products:
            if product.name:
                # Get the first product variant to link the channel
                product_variant = product.product_variant_ids[:1] if product.product_variant_ids else False
                if product_variant:
                    self.env['slide.channel'].create({
                        'name': product.name,
                        'product_id': product_variant.id,
                        'description': product.description or '',
                        'channel_type': 'training',
                    })
        
        return products

