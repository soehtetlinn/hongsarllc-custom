# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.exceptions import AccessError


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'
    
    def _visible_menu_ids(self, debug=False):
        """Override menu visibility based on department groups"""
        visible_ids = super()._visible_menu_ids(debug)
        
        if not self.env.user or self.env.user._is_superuser():
            return visible_ids
        
        # Get user's department
        user = self.env.user
        department = user.teaching_department_id
        
        if not department:
            return visible_ids
        
        department_name = department.name.lower()
        
        # Administration: Full access (do nothing)
        if department_name in ['administration', 'admin']:
            return visible_ids
        
        # Marketing: Only Marketing menus + Website with Restricted Content
        elif department_name == 'marketing':
            # Hide all menus except Marketing and Website (Restricted Content)
            # We'll hide menus that are NOT in marketing/website categories
            marketing_menus = self._get_marketing_menus()
            website_menus = self._get_website_restricted_menus()
            allowed_menus = marketing_menus | website_menus
            visible_ids = visible_ids & allowed_menus
        
        # Operations: Everything except Admin and Marketing
        elif department_name == 'operations':
            # Hide Admin and Marketing menus
            admin_menus = self._get_admin_menus()
            marketing_menus = self._get_marketing_menus()
            excluded_menus = admin_menus | marketing_menus
            visible_ids = visible_ids - excluded_menus
        
        # Teachers: eLearning, Sale, Chatting, Website Restricted, Course Assignment, Meeting, Appointment, Calendar, Tutoring
        elif department_name in ['teachers', 'teacher']:
            allowed_menus = (
                self._get_elearning_menus() |
                self._get_sale_menus() |
                self._get_chatting_menus() |
                self._get_website_restricted_menus() |
                self._get_meeting_menus() |
                self._get_appointment_menus() |
                self._get_calendar_menus() |
                self._get_tutoring_menus()
            )
            visible_ids = visible_ids & allowed_menus
        
        return visible_ids
    
    def _get_admin_menus(self):
        """Get admin/system configuration menus"""
        admin_menu_xmlids = [
            'base.menu_administration',
            'base.menu_security',
            'base.menu_custom',
        ]
        return self._get_menus_by_xmlids(admin_menu_xmlids)
    
    def _get_marketing_menus(self):
        """Get marketing related menus"""
        marketing_menu_xmlids = [
            'mass_mailing.menu_mass_mailing_root',
            'marketing_automation.menu_marketing_automation',
            'social.menu_social',
            'utm.menu_link_tracker_root',
            'website.menu_website',
        ]
        return self._get_menus_by_xmlids(marketing_menu_xmlids)
    
    def _get_elearning_menus(self):
        """Get eLearning menus"""
        elearning_menu_xmlids = [
            'website_slides.menu_website_slides_root',
            'website_slides.slide_channel_action_overview',
        ]
        return self._get_menus_by_xmlids(elearning_menu_xmlids)
    
    def _get_sale_menus(self):
        """Get Sale menus"""
        sale_menu_xmlids = [
            'sale.sale_menu_root',
            'sale.sale_order_menu',
            'sale.sale_report',
        ]
        return self._get_menus_by_xmlids(sale_menu_xmlids)
    
    def _get_chatting_menus(self):
        """Get Chatting/Discuss menus"""
        chatting_menu_xmlids = [
            'mail.menu_root_discuss',
            'mail.mail_channel_menu',
        ]
        return self._get_menus_by_xmlids(chatting_menu_xmlids)
    
    def _get_website_restricted_menus(self):
        """Get Website menus with restricted content"""
        website_menu_xmlids = [
            'website.menu_website',
            'website.menu_website_configuration',
        ]
        return self._get_menus_by_xmlids(website_menu_xmlids)
    
    def _get_meeting_menus(self):
        """Get Meeting menus"""
        meeting_menu_xmlids = [
            'calendar.mail_menu_calendar',
            'calendar.calendar_menu_root',
        ]
        return self._get_menus_by_xmlids(meeting_menu_xmlids)
    
    def _get_appointment_menus(self):
        """Get Appointment menus"""
        appointment_menu_xmlids = [
            'appointment.appointment_type_action',
        ]
        return self._get_menus_by_xmlids(appointment_menu_xmlids)
    
    def _get_calendar_menus(self):
        """Get Calendar menus (overlaps with meetings)"""
        return self._get_meeting_menus()
    
    def _get_tutoring_menus(self):
        """Get Tutoring module menus"""
        tutoring_menu_xmlids = [
            'tutoring_mod.menu_tutor_root',
        ]
        return self._get_menus_by_xmlids(tutoring_menu_xmlids)
    
    def _get_menus_by_xmlids(self, xmlids):
        """Get menu IDs by XML IDs including all descendants"""
        menu_ids = set()
        for xmlid in xmlids:
            menu_ref = self.env.ref(xmlid, raise_if_not_found=False)
            if menu_ref:
                # Get the menu and all its descendants recursively
                menu_ids.add(menu_ref.id)
                menu_ids.update(self._get_descendant_menu_ids(menu_ref.id))
        return menu_ids
    
    def _get_descendant_menu_ids(self, menu_id):
        """Recursively get all descendant menu IDs"""
        descendant_ids = set()
        children = self.search([('parent_id', '=', menu_id)])
        for child in children:
            descendant_ids.add(child.id)
            descendant_ids.update(self._get_descendant_menu_ids(child.id))
        return descendant_ids
    

