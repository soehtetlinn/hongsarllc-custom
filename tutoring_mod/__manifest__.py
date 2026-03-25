# -*- coding: utf-8 -*-
{
    'name': 'Tutoring Module',
    'version': '18.0',
    'category': 'Education',
    'summary': 'Manage Tutor Groups and Tutor Access Rights linked to Users, Departments, Products, and Courses',
    'description': """
Tutor Group and Access Rights
=============================

This module provides functionality to manage:
* User Types: Differentiate between Students, Tutors, and Operators
* Departments: Use HR Departments to organize users (tutors, students, operators)
* Tutor Groups: Group tutors together for better organization
* Tutor Access Rights: Control which tutors have access to which courses/products
* Links to res.users (login users/employees), hr.department, products, and courses (slide.channel)

Features:
---------
* User type classification (Student, Tutor, Operator)
* Uses existing HR Department model (hr.department) for organization
* Create and manage tutor groups linked to HR departments
* Assign tutors (only users with user_type='tutor') to groups
* Define access rights for tutors to courses and products
* Track which tutors have access to which resources
* Integrate with Odoo's user and HR management
* Link to products and courses (slide.channel)
* Partners automatically reflect tutor information from their related users

Note: 
* Only users with user_type='tutor' can be assigned to tutor groups and have access rights
* Tutors are login users/employees (res.users with share=False), not portal/public users
* Students and Operators are also login users but cannot be tutors
* Uses existing HR Department (hr.department) model - no custom department model needed

Author: Odoo Custom Module
    """,
    'author': 'Odoo Custom',
    'depends': [
        'base',
        'hr',
        'product',
        'website_slides',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/department_groups_data.xml',
        'views/user_department_wizard_views.xml',
        'views/hr_department_views.xml',
        'views/tutor_group_views.xml',
        'views/tutor_access_right_views.xml',
        'views/res_users_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

