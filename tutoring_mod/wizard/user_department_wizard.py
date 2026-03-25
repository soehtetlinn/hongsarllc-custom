# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class UserDepartmentWizard(models.TransientModel):
    _name = 'user.department.wizard'
    _description = 'Assign Users to Department'

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True,
        help='Select the department to assign users to'
    )
    
    user_ids = fields.Many2many(
        'res.users',
        'user_department_wizard_rel',
        'wizard_id',
        'user_id',
        string='Users',
        required=True,
        domain=[('share', '=', False)],
        help='Select users to assign to this department'
    )
    
    auto_assign_group = fields.Boolean(
        string='Automatically Assign Department Group',
        default=True,
        help='If checked, users will be automatically assigned to the department\'s access group'
    )

    def action_assign_department(self):
        """Assign selected users to the department"""
        self.ensure_one()
        
        if not self.user_ids:
            raise ValidationError(_('Please select at least one user.'))
        
        if not self.department_id:
            raise ValidationError(_('Please select a department.'))
        
        # Assign users to department
        self.user_ids.write({'teaching_department_id': self.department_id.id})
        
        # Auto-assign group if enabled
        if self.auto_assign_group and self.department_id.group_id:
            for user in self.user_ids:
                if self.department_id.group_id not in user.groups_id:
                    user.write({'groups_id': [(4, self.department_id.group_id.id)]})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Assigned %s user(s) to %s department.') % (len(self.user_ids), self.department_id.name),
                'type': 'success',
                'sticky': False,
            }
        }

