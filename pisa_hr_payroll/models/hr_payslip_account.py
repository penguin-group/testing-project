# -*- coding: utf-8 -*-

from collections import defaultdict
from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class HrPayslipAccount(models.Model):
    _inherit = 'hr.payslip'
    
    def _prepare_line_values(self, line, account_id, date, debit, credit):
        """Override to handle multi-currency accounting entries"""
        res = super()._prepare_line_values(line, account_id, date, debit, credit)
        
        # Multi-currency handling for contracts with different currency
        if self.contract_id and hasattr(self.contract_id, 'contract_currency_id'):
            contract_currency = self.contract_id.contract_currency_id
            company_currency = self.company_id.currency_id
            
            if contract_currency and contract_currency != company_currency:
                # Store original amounts in contract currency
                original_debit = debit
                original_credit = credit
                
                # Convert amounts to company currency for the accounting entries
                if debit:
                    res['debit'] = contract_currency._convert(
                        debit, company_currency, self.company_id, date
                    )
                if credit:
                    res['credit'] = contract_currency._convert(
                        credit, company_currency, self.company_id, date
                    )
                
                # Add multi-currency fields for proper foreign currency tracking
                res.update({
                    'currency_id': contract_currency.id,
                    'amount_currency': original_debit - original_credit,  # Original amount in contract currency
                })
                
        return res

    def _prepare_slip_lines(self, date, line_ids):
        """Override to handle currency conversion in payslip accounting lines"""
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Payroll')
        new_lines = []
        
        for line in self.line_ids.filtered(lambda line: line.category_id):
            amount = line.total
            if line.code == 'NET': # Check if the line is the 'Net Salary'.
                for tmp_line in self.line_ids.filtered(lambda line: line.category_id):
                    if tmp_line.salary_rule_id.not_computed_in_net: # Check if the rule must be computed in the 'Net Salary' or not.
                        if amount > 0:
                            amount -= abs(tmp_line.total)
                        elif amount < 0:
                            amount += abs(tmp_line.total)
            if float_is_zero(amount, precision_digits=precision):
                continue
                
            debit_account_id = line.salary_rule_id.account_debit.id
            credit_account_id = line.salary_rule_id.account_credit.id
            
            if debit_account_id: # If the rule has a debit account.
                debit = amount if amount > 0.0 else 0.0
                credit = -amount if amount < 0.0 else 0.0

                debit_line = next(self._get_existing_lines(
                    line_ids + new_lines, line, debit_account_id, debit, credit), False)

                if not debit_line:
                    debit_line = self._prepare_line_values(line, debit_account_id, date, debit, credit)
                    debit_line['tax_ids'] = [(4, tax_id) for tax_id in line.salary_rule_id.account_debit.tax_ids.ids]
                    new_lines.append(debit_line)
                else:
                    # Handle currency aggregation
                    contract_currency = self.contract_id.contract_currency_id or self.contract_id.currency_id
                    company_currency = self.company_id.currency_id
                    
                    if contract_currency != company_currency:
                        # Convert and add to existing line
                        debit_company = contract_currency._convert(debit, company_currency, self.company_id, date)
                        credit_company = contract_currency._convert(credit, company_currency, self.company_id, date)
                        debit_line['debit'] += debit_company
                        debit_line['credit'] += credit_company
                        debit_line['amount_currency'] = debit_line.get('amount_currency', 0) + (debit - credit)
                    else:
                        debit_line['debit'] += debit
                        debit_line['credit'] += credit

            if credit_account_id: # If the rule has a credit account.
                debit = -amount if amount < 0.0 else 0.0
                credit = amount if amount > 0.0 else 0.0
                credit_line = next(self._get_existing_lines(
                    line_ids + new_lines, line, credit_account_id, debit, credit), False)

                if not credit_line:
                    credit_line = self._prepare_line_values(line, credit_account_id, date, debit, credit)
                    credit_line['tax_ids'] = [(4, tax_id) for tax_id in line.salary_rule_id.account_credit.tax_ids.ids]
                    new_lines.append(credit_line)
                else:
                    # Handle currency aggregation
                    contract_currency = self.contract_id.contract_currency_id or self.contract_id.currency_id
                    company_currency = self.company_id.currency_id
                    
                    if contract_currency != company_currency:
                        # Convert and add to existing line
                        debit_company = contract_currency._convert(debit, company_currency, self.company_id, date)
                        credit_company = contract_currency._convert(credit, company_currency, self.company_id, date)
                        credit_line['debit'] += debit_company
                        credit_line['credit'] += credit_company
                        credit_line['amount_currency'] = credit_line.get('amount_currency', 0) + (debit - credit)
                    else:
                        credit_line['debit'] += debit
                        credit_line['credit'] += credit
                        
        return new_lines

    def _action_create_account_move(self):
        """Override to ensure proper currency handling in account moves"""
        # Multi-currency payroll accounting for Paraguay
        if self.env.company.country_code == 'PY':
            # Ensure all payslips in this batch use consistent currency handling
            for payslip in self:
                if payslip.contract_id and hasattr(payslip.contract_id, 'contract_currency_id'):
                    contract_currency = payslip.contract_id.contract_currency_id
                    company_currency = payslip.company_id.currency_id
                    
                    # Log currency information for debugging
                    if contract_currency != company_currency:
                        self.env['ir.logging'].sudo().create({
                            'name': 'pisa_hr_payroll.multi_currency',
                            'type': 'server',
                            'level': 'INFO',
                            'message': f'Processing multi-currency payslip {payslip.number}: '
                                     f'Contract {contract_currency.name} -> Company {company_currency.name}',
                            'path': 'pisa_hr_payroll.models.hr_payslip_account',
                            'func': '_action_create_account_move',
                            'line': '1',
                        })
        
        return super()._action_create_account_move()