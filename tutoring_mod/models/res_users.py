# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    # User type: student, tutor, operator
    user_type = fields.Selection(
        [
            ('student', 'Student'),
            ('tutor', 'Tutor'),
            ('operator', 'Operator'),
        ],
        string='User Type',
        default='student',
        required=True,
        index=True,
        help='Type of user: Student, Tutor, or Operator'
    )
    
    # Teaching department (using hr.department)
    teaching_department_id = fields.Many2one(
        'hr.department',
        string='Teaching Department',
        ondelete='restrict',
        index=True,
        help='Teaching department this user belongs to (uses HR Department)'
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Auto-assign user to department group on create"""
        users = super().create(vals_list)
        users._sync_department_group()
        return users
    
    def write(self, vals):
        """Auto-assign user to department group when department changes"""
        result = super().write(vals)
        if 'teaching_department_id' in vals:
            self._sync_department_group()
        return result
    
    def _sync_department_group(self):
        """Sync user's groups based on their department"""
        for user in self:
            if not user.teaching_department_id or not user.teaching_department_id.group_id:
                continue
            
            # Add department group to user
            if user.teaching_department_id.group_id not in user.groups_id:
                user.write({'groups_id': [(4, user.teaching_department_id.group_id.id)]})
    
    # Many2many relationship with tutor groups (only for tutors)
    tutor_group_ids = fields.Many2many(
        'tutor.group',
        'tutor_group_user_rel',
        'user_id',
        'tutor_group_id',
        string='Tutor Groups',
        help='Tutor groups this user belongs to (only for tutors)'
    )
    
    tutor_group_count = fields.Integer(
        string='Tutor Groups Count',
        compute='_compute_tutor_group_count'
    )
    
    # One2many relationship with tutor access rights (only for tutors)
    tutor_access_right_ids = fields.One2many(
        'tutor.access.right',
        'user_id',
        string='Tutor Access Rights',
        help='Access rights granted to this user as a tutor (only for tutors)'
    )
    
    tutor_access_right_count = fields.Integer(
        string='Access Rights Count',
        compute='_compute_tutor_access_right_count'
    )
    
    is_tutor = fields.Boolean(
        string='Is Tutor',
        compute='_compute_is_tutor',
        store=True,
        help='Check if this user is a tutor (user_type=tutor)'
    )
    
    @api.depends('tutor_group_ids')
    def _compute_tutor_group_count(self):
        for record in self:
            record.tutor_group_count = len(record.tutor_group_ids)
    
    @api.depends('tutor_access_right_ids')
    def _compute_tutor_access_right_count(self):
        for record in self:
            record.tutor_access_right_count = len(record.tutor_access_right_ids.filtered(lambda r: r.active))
    
    @api.depends('user_type')
    def _compute_is_tutor(self):
        for record in self:
            record.is_tutor = record.user_type == 'tutor'
    
    @api.constrains('user_type', 'tutor_group_ids', 'tutor_access_right_ids')
    def _check_tutor_restrictions(self):
        """Ensure only tutors can have tutor groups and access rights"""
        for record in self:
            if record.user_type != 'tutor':
                if record.tutor_group_ids:
                    raise ValidationError(
                        f'Only tutors can be assigned to tutor groups. '
                        f'User "{record.name}" is a {record.user_type}.'
                    )
                if record.tutor_access_right_ids:
                    raise ValidationError(
                        f'Only tutors can have tutor access rights. '
                        f'User "{record.name}" is a {record.user_type}.'
                    )
    
    def action_view_tutor_groups(self):
        """Open tutor groups for this user"""
        self.ensure_one()
        return {
            'name': 'Tutor Groups',
            'type': 'ir.actions.act_window',
            'res_model': 'tutor.group',
            'view_mode': 'list,form',
            'domain': [('user_ids', 'in', self.ids)],
        }
    
    def action_view_tutor_access_rights(self):
        """Open access rights for this user"""
        self.ensure_one()
        return {
            'name': 'Tutor Access Rights',
            'type': 'ir.actions.act_window',
            'res_model': 'tutor.access.right',
            'view_mode': 'list,form',
            'domain': [('user_id', '=', self.id)],
            'context': {'default_user_id': self.id},
        }

