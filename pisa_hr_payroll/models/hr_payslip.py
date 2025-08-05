# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # Paraguay-specific payslip fields
    location = fields.Char(
        string='Location',
        default='ASUNCION',
        help='Work location for payslip'
    )
    
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

    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
        """Override to add Paraguay-specific worked day types"""
        res = super()._get_worked_day_lines(domain, check_out_of_contract)
        
        # Add custom worked day line processing if needed
        return res

    def _get_base_local_dict(self):
        """Add Paraguay-specific functions to salary rule evaluation context"""
        res = super()._get_base_local_dict()
        
        res.update({
            'compute_family_allowance': self._compute_family_allowance,
            'compute_daycare_allowance': self._compute_daycare_allowance,
            'compute_overtime_night_surcharge': self._compute_overtime_night_surcharge,
        })
        
        return res

    def _compute_family_allowance(self, employee, contract):
        """Calculate family allowance based on children under 17"""
        if employee.children <= 0:
            return 0.0
            
        # Check salary limit (2 minimum wages)
        minimum_wage = self.env['hr.rule.parameter']._get_parameter_from_code(
            'minimum_wage_py', self.date_to, raise_if_not_found=False) or 2798309
        salary_limit = minimum_wage * 2
        
        # If salary exceeds limit, no family allowance
        if contract.wage > salary_limit:
            return 0.0
            
        # Calculate allowance per child
        allowance_per_child = self.env['hr.rule.parameter']._get_parameter_from_code(
            'family_allowance_per_child_py', self.date_to, raise_if_not_found=False) or 25000
            
        return employee.children * allowance_per_child

    def _compute_daycare_allowance(self, employee, contract):
        """Calculate daycare allowance for children under 3"""
        if employee.children_under_3 <= 0:
            return 0.0
            
        allowance_per_child = self.env['hr.rule.parameter']._get_parameter_from_code(
            'daycare_allowance_per_child_py', self.date_to, raise_if_not_found=False) or 30000
            
        return employee.children_under_3 * allowance_per_child

    def _compute_overtime_night_surcharge(self, base_amount):
        """Calculate 30% night surcharge on overtime"""
        return base_amount * 0.30