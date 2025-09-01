# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    
    def _check_payroll_closing_date(self):
        """Check if current date is after payroll closing day for the payslip period month"""
        for batch in self:
            if not batch.company_id.payroll_closing_day:
                continue  # Payroll closing disabled
                
            # Check current date against the closing date of the payslip period month
            today = fields.Date.today()
            # Use the end date of the batch to determine which month's closing date to check
            period_closing_date = batch.company_id.get_payroll_closing_date(batch.date_end)
            
            if period_closing_date and today <= period_closing_date:
                raise UserError(_(
                    "Cannot confirm batch '%s'.\n"
                    "Today (%s) is on or before the payroll closing day (%s) for the payslip period (%s).\n"
                    "Payroll operations for %s %s are only allowed after %s.\n\n"
                    "Please either:\n"
                    "• Wait until after %s to confirm this batch\n"
                    "• Contact your administrator to adjust the payroll closing day in Settings > Payroll"
                ) % (
                    batch.name,
                    today.strftime('%Y-%m-%d'),
                    period_closing_date.strftime('%Y-%m-%d'),
                    batch.date_end.strftime('%B %Y'),
                    batch.date_end.strftime('%B'),
                    batch.date_end.strftime('%Y'),
                    batch.company_id._get_closing_day_ordinal(),
                    period_closing_date.strftime('%Y-%m-%d')
                ))
    
    def action_confirm(self):
        """Override to add payroll closing date validation"""
        self._check_payroll_closing_date()
        return super().action_confirm()
    
    def action_validate(self):
        """Override to add payroll closing date validation"""
        self._check_payroll_closing_date()
        return super().action_validate()
    
    def action_open(self):
        """Override to add payroll closing date validation"""
        self._check_payroll_closing_date()
        return super().action_open()
    
    def action_close(self):
        """Override to add payroll closing date validation"""
        self._check_payroll_closing_date()
        return super().action_close()