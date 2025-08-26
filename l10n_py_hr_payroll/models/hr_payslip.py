# -*- coding: utf-8 -*-

from datetime import date, datetime
from collections import defaultdict
from odoo import api, fields, models, _
from odoo.tools import float_round
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # Paraguay-specific payslip fields
    location = fields.Char(
        string='Location',
        default='ASUNCION',
        help='Work location for payslip'
    )
    
    def _check_payroll_closing_date(self):
        """Check if current date is after payroll closing day for the payslip period month"""
        for payslip in self:
            if not payslip.company_id.payroll_closing_day:
                continue  # Payroll closing disabled
                
            # Check current date against the closing date of the payslip period month
            today = fields.Date.today()
            # Use the end date of the payslip to determine which month's closing date to check
            period_closing_date = payslip.company_id.get_payroll_closing_date(payslip.date_to)
            
            if period_closing_date and today <= period_closing_date:
                raise UserError(_(
                    "Cannot confirm payslip for %s.\n"
                    "Today (%s) is on or before the payroll closing day (%s) for the payslip period (%s).\n"
                    "Payroll operations for %s %s are only allowed after %s.\n\n"
                    "Please either:\n"
                    "• Wait until after %s to confirm this payslip\n"
                    "• Contact your administrator to adjust the payroll closing day in Settings > Payroll"
                ) % (
                    payslip.employee_id.name,
                    today.strftime('%Y-%m-%d'),
                    period_closing_date.strftime('%Y-%m-%d'),
                    payslip.date_to.strftime('%B %Y'),
                    payslip.date_to.strftime('%B'),
                    payslip.date_to.strftime('%Y'),
                    payslip.company_id._get_closing_day_ordinal(),
                    period_closing_date.strftime('%Y-%m-%d')
                ))
    
    def action_payslip_done(self):
        """Override to add payroll closing date validation"""
        self._check_payroll_closing_date()
        return super().action_payslip_done()
    
    area = fields.Char(
        related='employee_id.department_id.name',
        string='Area',
        help='Employee department/area'
    )
    
    currency_name = fields.Char(
        string='Currency Name',
        default='GUARANIES',
        help='Currency name for display on payslip'
    )
    
    cedula = fields.Char(
        related='employee_id.identification_id',
        string='Cédula',
        help='Employee identification number'
    )
    
    # Payment details
    payment_details = fields.Text(
        string='Payment Details',
        help='Details about how the payment was made (transfer, cash, etc.)'
    )
    
    # Currency handling for multi-currency contracts
    @api.depends('contract_id.contract_currency_id', 'contract_id.currency_id')
    def _compute_currency_id(self):
        """Override to ensure payslip uses contract currency"""
        for payslip in self:
            if payslip.contract_id and hasattr(payslip.contract_id, 'contract_currency_id'):
                payslip.currency_id = payslip.contract_id.contract_currency_id or payslip.contract_id.currency_id
            else:
                # Fallback to standard computation
                payslip.currency_id = payslip.contract_id.currency_id if payslip.contract_id else payslip.company_id.currency_id

    currency_id = fields.Many2one(related='contract_id.contract_currency_id')

    def _is_paraguayan_structure(self):
        self.ensure_one()
        return self.struct_id.get_external_id().get(self.struct_id.id) == 'pisa_hr_payroll.hr_payroll_structure_py_employee_salary'

    def _get_worked_day_lines_hours_per_day(self):
        """Override for Paraguay: Use calendar days instead of working days
        Paraguay law requires payroll calculation based on 30 calendar days per month
        """
        self.ensure_one()
        # Check if this is a Paraguayan payroll structure
        if self.struct_id and 'py' in self.struct_id.code.lower():
            # For Paraguay: fixed 8 hours per day (30 days * 8 hours = 240 hours per month)
            return 8.0
        return super()._get_worked_day_lines_hours_per_day()

    def _get_worked_day_lines_values(self, domain=None):
        """Enhanced worked day lines calculation with proper currency handling"""
        self.ensure_one()
        res = []
        hours_per_day = self._get_worked_day_lines_hours_per_day()
        work_hours = self.contract_id.get_work_hours(self.date_from, self.date_to, domain=domain)
        work_hours_ordered = sorted(work_hours.items(), key=lambda x: x[1])
        biggest_work = work_hours_ordered[-1][0] if work_hours_ordered else 0
        add_days_rounding = 0
        
        for work_entry_type_id, hours in work_hours_ordered:
            work_entry_type = self.env['hr.work.entry.type'].browse(work_entry_type_id)
            days = round(hours / hours_per_day, 5) if hours_per_day else 0
            if work_entry_type_id == biggest_work:
                days += add_days_rounding
            day_rounded = self._round_days(work_entry_type, days)
            add_days_rounding += (days - day_rounded)
            attendance_line = {
                'sequence': work_entry_type.sequence,
                'work_entry_type_id': work_entry_type_id,
                'number_of_days': day_rounded,
                'number_of_hours': hours,
            }
            res.append(attendance_line)

        # Sort by Work Entry Type sequence
        work_entry_type = self.env['hr.work.entry.type']
        return sorted(res, key=lambda d: work_entry_type.browse(d['work_entry_type_id']).sequence)

    def _get_localdict(self):
        """Override to add currency conversion utilities to salary rule calculations"""
        localdict = super()._get_localdict()
        
        # Add currency utilities for Paraguay payroll calculations
        if self.env.company.country_code == 'PY' and self.contract_id:
            contract_currency = getattr(self.contract_id, 'contract_currency_id', None) or self.contract_id.currency_id
            company_currency = self.company_id.currency_id
            
            # Add currency conversion utilities to localdict
            localdict.update({
                'contract_currency': contract_currency,
                'company_currency': company_currency,
                'convert_to_company': lambda amount: contract_currency._convert(
                    amount, company_currency, self.company_id, self.date_to or fields.Date.today()
                ) if contract_currency != company_currency else amount,
                'convert_from_company': lambda amount: company_currency._convert(
                    amount, contract_currency, self.company_id, self.date_to or fields.Date.today()
                ) if contract_currency != company_currency else amount,
            })
        
        return localdict


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'
    
    def _compute_amount(self):
        """Override to handle currency conversion for worked days amounts"""
        for worked_days in self:
            if worked_days.payslip_id.edited or worked_days.payslip_id.state not in ['draft', 'verify']:
                continue
            if not worked_days.contract_id or worked_days.code == 'OUT' or worked_days.is_credit_time:
                worked_days.amount = 0
                continue
                
            # Paraguay specific calculation for standard work days
            if (self.env.company.country_code == 'PY' and 
                worked_days.code == 'WORK100' or 'attendance' in str(worked_days.work_entry_type_id).lower()):
                # For Paraguay: Use fixed 30 days for monthly wage calculation
                if worked_days.payslip_id.wage_type == "hourly":
                    worked_days.amount = worked_days.payslip_id.contract_id.hourly_wage * worked_days.number_of_hours if worked_days.is_paid else 0
                else:
                    # Monthly wage divided by 30 days, multiplied by actual days
                    daily_wage = worked_days.payslip_id.contract_id.wage / 30.0
                    worked_days.amount = daily_wage * worked_days.number_of_days if worked_days.is_paid else 0
            else:
                # For non-Paraguayan structures, use default behavior
                super(HrPayslipWorkedDays, worked_days)._compute_amount()


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'
    
    def _get_amount_in_currency(self, target_currency, date=None):
        """Convert the payslip line amount to target currency"""
        self.ensure_one()
        if not date:
            date = self.slip_id.date_to or fields.Date.today()
        
        if self.currency_id == target_currency:
            return self.total
            
        return self.currency_id._convert(
            self.total, target_currency, self.company_id, date
        )