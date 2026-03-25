# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TutorGroup(models.Model):
    _name = 'tutor.group'
    _description = 'Tutor Group'
    _order = 'name'

    name = fields.Char(string='Group Name', required=True, index=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    
    # Links to res.users (only tutors)
    user_ids = fields.Many2many(
        'res.users',
        'tutor_group_user_rel',
        'tutor_group_id',
        'user_id',
        string='Tutors',
        help='Tutors (login users/employees with user_type=tutor) in this group'
    )
    
    # Teaching department (using hr.department)
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        ondelete='restrict',
        index=True,
        help='HR Department this tutor group belongs to'
    )
    
    # Links to products (courses/products this group has access to)
    product_ids = fields.Many2many(
        'product.product',
        'tutor_group_product_rel',
        'tutor_group_id',
        'product_id',
        string='Products',
        help='Products associated with this tutor group'
    )
    
    # Links to courses (slide.channel)
    course_ids = fields.Many2many(
        'slide.channel',
        'tutor_group_course_rel',
        'tutor_group_id',
        'course_id',
        string='Courses',
        help='Courses (slide.channel) associated with this tutor group'
    )
    
    # Related access rights
    access_right_ids = fields.One2many(
        'tutor.access.right',
        'tutor_group_id',
        string='Access Rights',
        help='Access rights defined for this tutor group'
    )
    
    access_right_count = fields.Integer(
        string='Access Rights Count',
        compute='_compute_access_right_count'
    )
    
    tutor_count = fields.Integer(
        string='Tutors Count',
        compute='_compute_tutor_count'
    )
    
    product_count = fields.Integer(
        string='Products Count',
        compute='_compute_product_count'
    )
    
    course_count = fields.Integer(
        string='Courses Count',
        compute='_compute_course_count'
    )
    
    @api.depends('access_right_ids')
    def _compute_access_right_count(self):
        for record in self:
            record.access_right_count = len(record.access_right_ids)
    
    @api.depends('user_ids')
    def _compute_tutor_count(self):
        for record in self:
            # Count tutors (login users/employees)
            record.tutor_count = len(record.user_ids)
    
    @api.depends('product_ids')
    def _compute_product_count(self):
        for record in self:
            record.product_count = len(record.product_ids)
    
    @api.depends('course_ids')
    def _compute_course_count(self):
        for record in self:
            record.course_count = len(record.course_ids)
    
    @api.onchange('user_ids')
    def _onchange_user_ids(self):
        """Validate that only tutors are added to tutor groups"""
        if self.user_ids:
            non_tutors = self.user_ids.filtered(lambda u: u.user_type != 'tutor')
            if non_tutors:
                return {
                    'warning': {
                        'title': 'Invalid User Type',
                        'message': f'The following users are not tutors: {", ".join(non_tutors.mapped("name"))}. Only tutors can be added to tutor groups.'
                    }
                }
    
    def action_view_access_rights(self):
        """Open access rights for this tutor group"""
        self.ensure_one()
        return {
            'name': 'Access Rights',
            'type': 'ir.actions.act_window',
            'res_model': 'tutor.access.right',
            'view_mode': 'list,form',
            'domain': [('tutor_group_id', '=', self.id)],
            'context': {'default_tutor_group_id': self.id},
        }
    
    def action_view_tutors(self):
        """Open tutors for this tutor group"""
        self.ensure_one()
        return {
            'name': 'Tutors',
            'type': 'ir.actions.act_window',
            'res_model': 'res.users',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.user_ids.ids)],
        }
    
    def action_view_products(self):
        """Open products for this tutor group"""
        self.ensure_one()
        return {
            'name': 'Products',
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.product_ids.ids)],
        }
    
    def action_view_courses(self):
        """Open courses for this tutor group"""
        self.ensure_one()
        return {
            'name': 'Courses',
            'type': 'ir.actions.act_window',
            'res_model': 'slide.channel',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.course_ids.ids)],
        }

