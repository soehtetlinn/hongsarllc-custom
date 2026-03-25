# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Aggregated tutor groups from related users, to be used in partner views
    tutor_group_ids = fields.Many2many(
        comodel_name='tutor.group',
        string='Tutor Groups',
        compute='_compute_tutor_group_ids',
        store=False,
        help='All tutor groups of the related user(s)'
    )

    # Aggregated access rights from related users, to be used in partner views
    tutor_access_right_ids = fields.Many2many(
        comodel_name='tutor.access.right',
        string='Tutor Access Rights',
        compute='_compute_tutor_access_right_ids',
        store=False,
        help='All tutor access rights of the related user(s)'
    )

    # Computed fields based on related user being a tutor
    tutor_group_count = fields.Integer(
        string='Tutor Groups Count',
        compute='_compute_tutor_info',
        help='Number of tutor groups the related user belongs to (if user is a tutor)'
    )
    
    tutor_access_right_count = fields.Integer(
        string='Access Rights Count',
        compute='_compute_tutor_info',
        help='Number of access rights the related user has (if user is a tutor)'
    )
    
    is_tutor = fields.Boolean(
        string='Is Tutor',
        compute='_compute_tutor_info',
        store=False,
        help='Check if the related user is a tutor (login user/employee)'
    )
    
    @api.depends('user_ids.is_tutor', 'user_ids.tutor_group_ids', 'user_ids.tutor_access_right_ids')
    def _compute_tutor_info(self):
        for record in self:
            # Check if any related user is a tutor
            users = record.user_ids.filtered('is_tutor')
            record.is_tutor = bool(users)
            if users:
                record.tutor_group_count = len(users.mapped('tutor_group_ids'))
                record.tutor_access_right_count = len(users.mapped('tutor_access_right_ids').filtered(lambda r: r.active))
            else:
                record.tutor_group_count = 0
                record.tutor_access_right_count = 0

    def _compute_tutor_group_ids(self):
        for record in self:
            # Aggregate all tutor groups from all related users
            record.tutor_group_ids = [(6, 0, record.user_ids.mapped('tutor_group_ids').ids)]

    def _compute_tutor_access_right_ids(self):
        for record in self:
            # Aggregate all tutor access rights from all related users
            record.tutor_access_right_ids = [(6, 0, record.user_ids.mapped('tutor_access_right_ids').ids)]
    
    def action_view_tutor_groups(self):
        """Open tutor groups for related user(s)"""
        self.ensure_one()
        users = self.user_ids.filtered('is_tutor')
        if not users:
            return False
        return {
            'name': 'Tutor Groups',
            'type': 'ir.actions.act_window',
            'res_model': 'tutor.group',
            'view_mode': 'list,form',
            'domain': [('user_ids', 'in', users.ids)],
        }
    
    def action_view_tutor_access_rights(self):
        """Open access rights for related user(s)"""
        self.ensure_one()
        users = self.user_ids.filtered('is_tutor')
        if not users:
            return False
        return {
            'name': 'Tutor Access Rights',
            'type': 'ir.actions.act_window',
            'res_model': 'tutor.access.right',
            'view_mode': 'list,form',
            'domain': [('user_id', 'in', users.ids)],
        }

