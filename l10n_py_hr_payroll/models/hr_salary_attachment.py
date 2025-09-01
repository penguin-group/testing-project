# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrSalaryAttachment(models.Model):
    _inherit = 'hr.salary.attachment'

    # Attachment-specific currency field (separate from company currency)
    attachment_currency_id = fields.Many2one(
        'res.currency', 
        string="Attachment Currency", 
        default=lambda self: self.env.company.currency_id,
        required=True,
        help="Currency for this salary attachment. Can be different from company currency."
    )
    
    # Override currency_id to use attachment currency for payroll
    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        compute='_compute_currency_id',
        store=True,
        help="Currency used for payroll calculations (from attachment currency)"
    )
    
    # Add computed field to show if attachment uses different currency than company
    is_multi_currency = fields.Boolean(
        string='Multi-Currency',
        compute='_compute_is_multi_currency',
        search='_search_is_multi_currency',
        help="True if attachment currency differs from company currency"
    )
    
    # Override monetary fields to use attachment currency
    monthly_amount = fields.Monetary(
        'Payslip Amount', 
        required=True, 
        tracking=True, 
        currency_field='attachment_currency_id',
        help='Amount to pay each payslip in attachment currency.'
    )
    
    total_amount = fields.Monetary(
        'Total Amount',
        tracking=True,
        currency_field='attachment_currency_id',
        help='Total amount to be paid in attachment currency.',
    )
    
    paid_amount = fields.Monetary(
        'Paid Amount', 
        tracking=True,
        currency_field='attachment_currency_id'
    )
    
    # Add field to display converted amounts in company currency for reference
    monthly_amount_company = fields.Monetary(
        string='Monthly Amount (Company Currency)',
        compute='_compute_amounts_in_company_currency',
        currency_field='company_currency_id',
        help='Payslip Amount in company currency for reference',
        readonly=True
    )
    
    total_amount_company = fields.Monetary(
        string='Total Amount (Company Currency)',
        compute='_compute_amounts_in_company_currency',
        currency_field='company_currency_id',
        help='Total amount in company currency for reference',
        readonly=True
    )
    
    company_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string='Company Currency'
    )
    
    # Override the currency_id to use our attachment currency
    @api.depends('attachment_currency_id')
    def _compute_currency_id(self):
        """Override currency_id to use attachment currency for payroll"""
        for attachment in self:
            attachment.currency_id = attachment.attachment_currency_id or attachment.company_id.currency_id

    @api.depends('attachment_currency_id', 'company_id.currency_id')
    def _compute_is_multi_currency(self):
        """Check if attachment uses different currency than company"""
        for attachment in self:
            attachment.is_multi_currency = (
                attachment.attachment_currency_id and 
                attachment.company_id.currency_id and
                attachment.attachment_currency_id != attachment.company_id.currency_id
            )
    
    def _search_is_multi_currency(self, operator, value):
        """Search method for is_multi_currency field"""
        # Since we can't easily compare attachment_currency_id != company_id.currency_id in domain,
        # we'll do a custom search by fetching all records and filtering
        all_attachments = self.search([])
        result_ids = []
        
        for attachment in all_attachments:
            is_multi = (
                attachment.attachment_currency_id and 
                attachment.company_id.currency_id and
                attachment.attachment_currency_id != attachment.company_id.currency_id
            )
            
            if (operator == '=' and value == is_multi) or \
               (operator == '!=' and value != is_multi):
                result_ids.append(attachment.id)
        
        return [('id', 'in', result_ids)]
    
    @api.depends('monthly_amount', 'total_amount', 'attachment_currency_id', 'company_id.currency_id')
    def _compute_amounts_in_company_currency(self):
        """Convert amounts to company currency for reference"""
        for attachment in self:
            if attachment.is_multi_currency:
                # Use latest exchange rate for display purposes
                rate_date = fields.Date.today()
                attachment.monthly_amount_company = attachment.attachment_currency_id._convert(
                    attachment.monthly_amount,
                    attachment.company_id.currency_id,
                    attachment.company_id,
                    rate_date
                )
                attachment.total_amount_company = attachment.attachment_currency_id._convert(
                    attachment.total_amount,
                    attachment.company_id.currency_id,
                    attachment.company_id,
                    rate_date
                )
            else:
                attachment.monthly_amount_company = attachment.monthly_amount
                attachment.total_amount_company = attachment.total_amount
    
    def get_amount_for_payslip(self, payslip):
        """
        Get the attachment amount converted to payslip currency using payroll closing date rate
        
        Args:
            payslip: hr.payslip record
            
        Returns:
            float: Amount in payslip currency using payroll closing date exchange rate
        """
        self.ensure_one()
        
        # If currencies are the same, no conversion needed
        if self.currency_id == payslip.currency_id:
            return self.monthly_amount
        
        # Get payroll closing date for the exchange rate
        closing_date = payslip.company_id.get_payroll_closing_date(payslip.date_to)
        
        # If no closing date configured, use payslip end date
        rate_date = closing_date or payslip.date_to or fields.Date.today()
        
        # Convert using the payroll closing date rate
        converted_amount = self.attachment_currency_id._convert(
            self.monthly_amount,
            payslip.currency_id,
            payslip.company_id,
            rate_date
        )
        
        return converted_amount
    
    @api.model
    def _get_attachment_amounts_for_payslip(self, payslip, input_type_codes):
        """
        Get attachment amounts for given input types, converted to payslip currency
        
        Args:
            payslip: hr.payslip record
            input_type_codes: list of input type codes to filter attachments
            
        Returns:
            dict: {input_code: total_converted_amount}
        """
        if not payslip.employee_id.salary_attachment_ids:
            return {}
        
        # Filter active attachments for the payslip period
        attachments = payslip.employee_id.salary_attachment_ids.filtered(
            lambda a: a.state == 'open' and 
                     a.date_start <= payslip.date_to and
                     (not a.date_end or a.date_end >= payslip.date_from) and
                     a.other_input_type_id.code in input_type_codes
        )
        
        result = {}
        for attachment in attachments:
            input_code = attachment.other_input_type_id.code
            converted_amount = attachment.get_amount_for_payslip(payslip)
            
            # Apply refund flag
            if attachment.is_refund:
                converted_amount = -converted_amount
            
            # Sum amounts for the same input type
            if input_code in result:
                result[input_code] += converted_amount
            else:
                result[input_code] = converted_amount
        
        return result
