# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    chatter_position = fields.Selection(
        [
            ('auto', 'Automatic (based on screen size)'),
            ('aside', 'Always beside form'),
            ('down', 'Always below form'),
        ],
        string='Chatter Position',
        default='auto',
        help='Control where the chatter (messages, followers) appears in form views.',
    )
