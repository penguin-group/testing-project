# -*- coding: utf-8 -*-

from datetime import date, datetime
from collections import defaultdict
from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    # Paraguay-specific contract fields  
    # Most deductions/allowances are now handled via Salary Attachments
    # This keeps the contract model clean and uses standard Odoo workflows
    
    # Contract-specific currency field (separate from company currency)
    contract_currency_id = fields.Many2one(
        'res.currency', 
        string="Contract Currency", 
        default=lambda self: self.env.company.currency_id,
        required=True,
        help="Currency for this contract. Can be different from company currency."
    )
    
    # Override currency_id to use contract currency for payroll
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        compute='_compute_currency_id',
        store=True,
        help="Currency used for payroll calculations (from contract currency)"
    )

    end_reason = fields.Char(
        string="End Reason"
    )
    branch_id = fields.Many2one(
        'res.company',
        domain="[('parent_id', '=', company_id)]",
        string="Branch",
        help="Branch associated with this contract"
    )
    
    # Override the currency_id to use our contract currency
    @api.depends('contract_currency_id')
    def _compute_currency_id(self):
        """Override currency_id to use contract currency for payroll"""
        for contract in self:
            contract.currency_id = contract.contract_currency_id or contract.company_id.currency_id
    
    # Override wage field to explicitly use contract currency
    wage = fields.Monetary(
        'Wage', 
        required=True, 
        tracking=True, 
        currency_field='contract_currency_id',
        help="Employee's monthly gross wage in contract currency.", 
        aggregator="avg"
    )
    
    def _convert_currency_amount(self, amount, target_currency=None, date=None):
        """Convert amount from contract currency to target currency"""
        self.ensure_one()
        if not target_currency:
            target_currency = self.company_id.currency_id
        if not date:
            date = fields.Date.today()
            
        if self.contract_currency_id == target_currency:
            return amount
            
        return self.contract_currency_id._convert(
            amount, target_currency, self.company_id, date
        )
    
    def _get_wage_in_company_currency(self, date=None):
        """Get the contract wage converted to company currency"""
        self.ensure_one()
        return self._convert_currency_amount(self.wage, self.company_id.currency_id, date)

    def get_work_hours(self, date_from, date_to, domain=None):
        # Paraguay-specific logic: 30 days worked, 8 hours each day
        if self.env.company.country_code == 'PY':
            work_data = defaultdict(int)
            # Use the default work entry type from the structure (standard working hours)
            # This represents calendar-based work hours, not attendance-based tracking
            default_work_entry_type = (
                self.structure_type_id.default_work_entry_type_id or 
                self.env.ref('hr_work_entry.work_entry_type_attendance', raise_if_not_found=False)
            )
            if default_work_entry_type:
                # 30 days × 8 hours = 240 hours (Paraguay standard)
                work_data[default_work_entry_type.id] = 240.0
            return work_data
        
        # For non-Paraguay companies, use the standard behavior
        return super().get_work_hours(date_from, date_to, domain=domain)