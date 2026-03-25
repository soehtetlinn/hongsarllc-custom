# -*- coding: utf-8 -*-
from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        session_info = super().session_info()
        user = self.env.user
        if self.env.uid:
            session_info['chatter_position'] = user.chatter_position or 'auto'
            IrConfigSudo = self.env['ir.config_parameter'].sudo()
            session_info['list_sticky_columns'] = int(
                IrConfigSudo.get_param('web_ux.list_sticky_columns', default='1')
            )
        return session_info
