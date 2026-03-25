# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    chatter_position = fields.Selection(
        [
            ('auto', 'Automatic (based on screen size)'),
            ('aside', 'Always beside form'),
            ('down', 'Always below form'),
        ],
        string='Chatter Position',
        help='Control where the chatter (messages, followers) appears in form views.',
    )
    list_sticky_columns = fields.Integer(
        string='Sticky Columns in List View',
        default=1,
        config_parameter='web_ux.list_sticky_columns',
        help='Number of left columns to keep fixed when scrolling horizontally (0 to disable).',
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        user = self.env.user
        res['chatter_position'] = user.chatter_position or 'auto'
        return res

    def set_values(self):
        super().set_values()
        for record in self:
            if record.chatter_position:
                record.env.user.chatter_position = record.chatter_position
