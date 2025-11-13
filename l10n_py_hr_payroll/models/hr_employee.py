# -*- coding: utf-8 -*-
from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    profession = fields.Char(string="Profession")
    minor_employee_school_status = fields.Char(
        string="Minor's school situation, if applicable",
        help="Minor's school situation, if applicable"
    )
