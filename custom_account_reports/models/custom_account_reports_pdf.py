# pylint: disable=missing-module-docstring,no-name-in-module

import base64
from odoo import models

PISA_COMPANY_ID = 1
PASA_COMPANY_ID = 2
# Only need to change the format of this 2 companies

class CustomAccountReportsXlsx(models.Model):
    """ Inherit account.reports to make a custom format for the reports
    """

    _inherit = "account.report"

    def get_company_logo(self):
        """ Get the company logo
        """

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        return base_url + '/web/image/res.company/' + str(self.env.company.id) + '/logo'

    def get_company_primary_color(self):
        """ Get the company primary color
        """

        return self.env.company.primary_color

    def get_company_styles(self):
        """ Get the company styles
        """

        primary_color = self.get_company_primary_color()

        return (
            f"background-color: {primary_color};"
            f"color: {'black' if primary_color == 'gray' else 'white'};"
        )
