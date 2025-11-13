# -*- coding: utf-8 -*-

from datetime import date, datetime
from collections import defaultdict
from odoo import api, fields, models, _
from odoo.tools import float_round
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
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
            
            # Add multi-currency salary attachment utilities
            localdict.update({
                'get_attachment_amount': self._get_attachment_amount_for_input_code,
                'get_attachment_amounts': self._get_attachment_amounts_for_input_codes,
            })
        
        return localdict
    
    def _get_attachment_amount_for_input_code(self, input_code):
        """
        Get converted salary attachment amount for a specific input code
        
        Args:
            input_code (str): Input type code (e.g., 'SALARY_ADVANCE', 'MEDICAL_INSURANCE')
            
        Returns:
            float: Total converted amount for the input code using payroll closing date rate
        """
        if not self.employee_id.salary_attachment_ids:
            return 0.0
        
        attachment_model = self.env['hr.salary.attachment']
        amounts = attachment_model._get_attachment_amounts_for_payslip(self, [input_code])
        return amounts.get(input_code, 0.0)
    
    def _get_attachment_amounts_for_input_codes(self, input_codes):
        """
        Get converted salary attachment amounts for multiple input codes
        
        Args:
            input_codes (list): List of input type codes
            
        Returns:
            dict: {input_code: converted_amount} using payroll closing date rates
        """
        if not self.employee_id.salary_attachment_ids:
            return {}
        
        attachment_model = self.env['hr.salary.attachment']
        return attachment_model._get_attachment_amounts_for_payslip(self, input_codes)

    def _get_payslip_lines(self):
        line_vals = super()._get_payslip_lines()
        currency_by_slip = {payslip.id: payslip.currency_id for payslip in self}
        for line in line_vals:
            slip_currency = currency_by_slip.get(line.get('slip_id'))
            if not slip_currency:
                continue
            rounding_digits = 0 if slip_currency.name == 'PYG' else 2
            line['amount'] = round(line['amount'], rounding_digits)
            line['total'] = round(line['total'], rounding_digits)
        return line_vals
    
    def _prepare_adjust_line(self, line_ids, adjust_type, debit_sum, credit_sum, date):
        acc_id = self.sudo().journal_id.default_account_id.id
        if not acc_id:
            raise UserError(_('The Expense Journal "%s" has not properly configured the default Account!', self.journal_id.name))
        existing_adjustment_line = (
            line_id for line_id in line_ids if line_id['name'] == self.env._('Adjustment Entry')
        )
        adjust_credit = next(existing_adjustment_line, False)
                    
        amount_currency_sum = 0
        for line_id in line_ids:
            amount_currency_sum += line_id.get('amount_currency', 0)

        adjust_credit = {
            'name': _('Adjustment Entry - Net Payable'),
            'partner_id': False,
            'account_id': acc_id,
            'journal_id': self.journal_id.id,
            'date': date,
            'currency_id': self.currency_id.id,
            'amount_currency': -amount_currency_sum if amount_currency_sum else credit_sum - debit_sum,
            'debit': 0.0 if adjust_type == 'credit' else credit_sum - debit_sum,
            'credit': debit_sum - credit_sum if adjust_type == 'credit' else 0.0,
        }
        line_ids.append(adjust_credit)


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