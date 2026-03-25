# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    # Link department to Odoo group
    group_id = fields.Many2one(
        'res.groups',
        string='Access Group',
        help='Odoo group linked to this department. Users in this department will be automatically assigned to this group.'
    )
    
    # Users in this department (for tutoring module)
    user_ids = fields.One2many(
        'res.users',
        'teaching_department_id',
        string='Users',
        help='Users (tutors, students, operators) in this department'
    )
    
    tutor_ids = fields.Many2many(
        'res.users',
        'hr_department_tutor_rel',
        'department_id',
        'user_id',
        string='Tutors',
        help='Tutors in this department (users with user_type=tutor)'
    )
    
    tutor_count = fields.Integer(
        string='Tutors Count',
        compute='_compute_user_counts'
    )
    
    student_count = fields.Integer(
        string='Students Count',
        compute='_compute_user_counts'
    )
    
    operator_count = fields.Integer(
        string='Operators Count',
        compute='_compute_user_counts'
    )
    
    @api.depends('user_ids', 'user_ids.user_type')
    def _compute_user_counts(self):
        for record in self:
            record.tutor_count = len(record.user_ids.filtered(lambda u: u.user_type == 'tutor'))
            record.student_count = len(record.user_ids.filtered(lambda u: u.user_type == 'student'))
            record.operator_count = len(record.user_ids.filtered(lambda u: u.user_type == 'operator'))
    
    def write(self, vals):
        """Sync users to group when department group changes"""
        result = super().write(vals)
        if 'group_id' in vals:
            self._sync_users_to_group()
        return result
    
    def _sync_users_to_group(self):
        """Automatically assign users to department's group"""
        for department in self:
            if not department.group_id:
                continue
            
            # Get all users in this department
            users = department.user_ids.filtered(lambda u: u.active)
            
            # Add department group to users
            for user in users:
                if department.group_id not in user.groups_id:
                    user.write({'groups_id': [(4, department.group_id.id)]})
            
            # Remove group from users not in this department
            # (but only if they don't belong to another department with the same group)
            group_users = department.group_id.users.filtered(lambda u: u.active)
            for user in group_users:
                if user not in users:
                    # Check if user belongs to another department with this group
                    other_dept = self.search([
                        ('group_id', '=', department.group_id.id),
                        ('id', '!=', department.id)
                    ])
                    if user not in other_dept.mapped('user_ids'):
                        user.write({'groups_id': [(3, department.group_id.id)]})
    
    @api.model
    def _link_department_to_group(self, domain, group_id):
        """Helper method to link existing department to group (used in data file)"""
        department = self.search(domain, limit=1)
        if department:
            department.write({'group_id': group_id})
            # Sync users to group
            department._sync_users_to_group()
            return department
        return False

