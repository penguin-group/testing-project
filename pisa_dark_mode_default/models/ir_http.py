# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def webclient_rendering_context(self):
        """
        Override to set dark mode as default and provide context for template.
        """
        result = super().webclient_rendering_context()
        
        # Check if user has no color scheme preference
        no_preference = not request.cookies.get('color_scheme')
        
        if request and no_preference:
            # Set dark mode cookie for future requests
            request.future_response.set_cookie(
                'color_scheme', 
                'dark',
                max_age=60 * 60 * 24 * 365,  # 1 year
                httponly=False,  # Allow JavaScript access for theme switching
                samesite='Lax'  # Security setting
            )
        
        # Provide context variable for immediate dark mode application
        result['default_dark_mode'] = no_preference
        
        return result 