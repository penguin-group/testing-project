# -*- coding: utf-8 -*-

import calendar
from datetime import date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    # Payroll Closing Day Configuration (e.g., 20 = 20th of each month)
    payroll_closing_day = fields.Integer(
        string="Payroll Closing Day",
        default=0,
        help="Day of each month when payroll closes (e.g., 20 = 20th of each month). "
             "No payroll operations can be confirmed before this day each month. "
             "Set to 0 to disable payroll closing protection."
    )

    ips_patronal_number = fields.Char(string="Patronal Number IPS")
    mtess_patronal_number = fields.Char(string="Patronal Number MTESS")
    
    @api.constrains('payroll_closing_day')
    def _check_payroll_closing_day(self):
        """Validate that the closing day is valid"""
        for company in self:
            if company.payroll_closing_day < 0 or company.payroll_closing_day > 31:
                raise ValidationError(
                    "Payroll closing day must be between 0 and 31. "
                    "Use 0 to disable payroll closing protection."
                )
    
    def get_payroll_closing_date(self, target_date=None):
        """Get the effective payroll closing date for a given date
        
        Args:
            target_date (date): The date to check against. Defaults to today.
            
        Returns:
            date or False: The closing date for the month containing target_date,
                          or False if payroll closing is disabled (day = 0)
        """
        self.ensure_one()
        if not self.payroll_closing_day:
            return False
            
        if not target_date:
            target_date = fields.Date.today()
        
        # Get the month and year from target date
        year = target_date.year
        month = target_date.month
        
        # Calculate the maximum day for this month
        max_day = calendar.monthrange(year, month)[1]
        
        # Use the minimum of closing day and max days in month
        closing_day = min(self.payroll_closing_day, max_day)
        
        return date(year, month, closing_day)
    
    def _get_closing_day_ordinal(self):
        """Get ordinal representation of closing day (e.g., 20th, 1st, 22nd)"""
        self.ensure_one()
        if not self.payroll_closing_day:
            return ""
        
        day = self.payroll_closing_day
        if 10 <= day % 100 <= 20:  # Special case for 11th, 12th, 13th
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        
        return f"{day}{suffix}"