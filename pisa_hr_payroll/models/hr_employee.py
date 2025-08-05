# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    # Paraguay-specific fields
    ips_number = fields.Char(
        string='IPS Number',
        help='Social Security (IPS) identification number for Paraguay'
    )