# -*- coding: utf-8 -*-
from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends('categ_id', 'categ_id.complete_name', 'create_uid', 'create_uid.name')
    def _compute_default_code(self):
        """Compute default_code based on category initials, creator initials, and sequence
        
        Format: CSM_Tu001
        - CSM: Category initials (excluding "All")
        - Tu: User initials (first 2 chars of create_uid.name)
        - 001: Sequence number based on category + creator combination
        """
        for record in self:
            # Part 1: Extract category initials, excluding "All"
            category_code = ""
            if record.categ_id and record.categ_id.complete_name:
                # Split by " / " and filter out "All"
                category_parts = [
                    p.strip() for p in record.categ_id.complete_name.split(" / ")
                    if p.strip().lower() != "all"
                ]
                # Get first letter of each remaining part (uppercase)
                category_code = "".join([
                    part[0].upper() for part in category_parts if part
                ])

            # Part 2: Extract user initials (first 2 chars, lowercase)
            user_code = ""
            # Use create_uid if available, otherwise use current user (for new records)
            user = record.create_uid or self.env.user
            if user and user.name:
                user_name = user.name.strip().lower()
                if len(user_name) >= 2:
                    user_code = user_name[:2]
                elif len(user_name) == 1:
                    user_code = user_name + "x"  # Pad single char with 'x'

            # Part 3: Generate sequence number (001, 002, etc.)
            # Check if codes exist and find the next available sequence
            sequence_num = "001"
            if category_code and user_code:
                base_code = f"{category_code}_{user_code}"
                # Try sequences starting from 001 until we find one that doesn't exist
                for seq in range(1, 1000):  # Max 999 products
                    candidate_code = f"{base_code}{str(seq).zfill(3)}"
                    # Check if this code already exists
                    domain = [('default_code', '=', candidate_code)]
                    # Exclude current record if it exists
                    if record.id:
                        domain.append(('id', '!=', record.id))
                    
                    exists = self.env['product.template'].search_count(domain, limit=1)
                    if not exists:
                        sequence_num = str(seq).zfill(3)
                        break

            # Combine: CSM_Tu001
            if category_code and user_code:
                record.default_code = f"{category_code}_{user_code}{sequence_num}"
            else:
                # If missing required data, try to get from variant or leave empty
                if not record.default_code:
                    # Fallback: call parent compute for variants if needed
                    if record.product_variant_ids and len(record.product_variant_ids) == 1:
                        record.default_code = record.product_variant_ids[0].default_code or ""
                    else:
                        record.default_code = ""

