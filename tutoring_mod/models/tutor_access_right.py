# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class TutorAccessRight(models.Model):
    _name = 'tutor.access.right'
    _description = 'Tutor Access Right'
    _order = 'date_granted desc, id desc'

    name = fields.Char(
        string='Access Right Name',
        compute='_compute_name',
        store=True,
        readonly=True
    )
    
    # Link to tutor group
    tutor_group_id = fields.Many2one(
        'tutor.group',
        string='Tutor Group',
        ondelete='cascade',
        required=True,
        index=True
    )
    
    # Link to individual tutor (login user/employee)
    user_id = fields.Many2one(
        'res.users',
        string='Tutor',
        ondelete='cascade',
        index=True,
        domain=[('share', '=', False)],
        help='Tutor (login user/employee with user_type=tutor) (optional if group is specified)'
    )
    
    # Link to product
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        ondelete='cascade',
        index=True,
        help='Product this access right applies to'
    )
    
    # Link to product template
    product_template_id = fields.Many2one(
        'product.template',
        string='Product Template',
        ondelete='cascade',
        index=True,
        help='Product template this access right applies to'
    )
    
    # Link to course (slide.channel)
    course_id = fields.Many2one(
        'slide.channel',
        string='Course',
        ondelete='cascade',
        index=True,
        help='Course (slide.channel) this access right applies to'
    )
    
    # Access right details
    access_type = fields.Selection(
        [
            ('read', 'Read Only'),
            ('write', 'Read/Write'),
            ('full', 'Full Access'),
            ('instructor', 'Instructor'),
        ],
        string='Access Type',
        default='read',
        required=True,
        help='Type of access granted'
    )
    
    date_granted = fields.Datetime(
        string='Date Granted',
        default=fields.Datetime.now,
        required=True,
        help='Date and time when this access was granted'
    )
    
    date_expires = fields.Datetime(
        string='Expiry Date',
        help='Date when this access expires (leave empty for no expiration)'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Whether this access right is currently active'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes about this access right'
    )
    
    # Computed fields for better identification
    tutor_name = fields.Char(
        string='Tutor Name',
        compute='_compute_tutor_name',
        store=True
    )
    
    resource_name = fields.Char(
        string='Resource',
        compute='_compute_resource_name',
        store=True
    )
    
    is_expired = fields.Boolean(
        string='Expired',
        compute='_compute_is_expired',
        store=True
    )
    
    @api.depends('tutor_group_id', 'user_id')
    def _compute_tutor_name(self):
        for record in self:
            names = []
            if record.tutor_group_id:
                names.append(f"Group: {record.tutor_group_id.name}")
            if record.user_id:
                names.append(f"Tutor: {record.user_id.name}")
            record.tutor_name = " | ".join(names) if names else "No Tutor"
    
    @api.depends('product_id', 'product_template_id', 'course_id')
    def _compute_resource_name(self):
        for record in self:
            names = []
            if record.product_id:
                names.append(f"Product: {record.product_id.name}")
            if record.product_template_id:
                names.append(f"Template: {record.product_template_id.name}")
            if record.course_id:
                names.append(f"Course: {record.course_id.name}")
            record.resource_name = " | ".join(names) if names else "No Resource"
    
    @api.depends('date_expires', 'active')
    def _compute_is_expired(self):
        now = fields.Datetime.now()
        for record in self:
            record.is_expired = (
                record.date_expires and
                record.date_expires < now
            ) if record.date_expires else False
    
    @api.depends('tutor_name', 'resource_name', 'access_type')
    def _compute_name(self):
        for record in self:
            parts = []
            if record.tutor_name:
                parts.append(record.tutor_name)
            if record.resource_name:
                parts.append(record.resource_name)
            if record.access_type:
                parts.append(f"[{dict(record._fields['access_type'].selection).get(record.access_type)}]")
            record.name = " - ".join(parts) if parts else "Access Right"
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Set product_template_id when product_id changes"""
        if self.product_id:
            self.product_template_id = self.product_id.product_tmpl_id
    
    @api.onchange('product_template_id')
    def _onchange_product_template_id(self):
        """Clear product_id when product_template_id changes"""
        if self.product_template_id and self.product_id:
            if self.product_id.product_tmpl_id != self.product_template_id:
                self.product_id = False
    
    @api.onchange('user_id')
    def _onchange_user_id(self):
        """Validate that only tutors are assigned"""
        if self.user_id and self.user_id.user_type != 'tutor':
            self.user_id = False
            return {
                'warning': {
                    'title': 'Invalid User Type',
                    'message': 'Only users with user_type="tutor" can be assigned as tutors.'
                }
            }
    
    @api.model
    def _cron_check_expired_access(self):
        """Cron job to deactivate expired access rights"""
        now = fields.Datetime.now()
        expired = self.search([
            ('active', '=', True),
            ('date_expires', '!=', False),
            ('date_expires', '<', now)
        ])
        expired.write({'active': False})

