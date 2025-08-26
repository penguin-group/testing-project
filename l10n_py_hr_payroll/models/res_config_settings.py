# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # Payroll Closing Day (monthly)
    payroll_closing_day = fields.Integer(
        string="Payroll Closing Day",
        related='company_id.payroll_closing_day',
        readonly=False,
        help="Day of each month when payroll closes (e.g., 20 = 20th of each month). "
             "No payroll operations can be confirmed before this day each month. "
             "Set to 0 to disable payroll closing protection."
    )