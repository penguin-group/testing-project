# -*- coding: utf-8 -*-

from odoo import fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    # Paraguay-specific contract fields  
    # Most deductions/allowances are now handled via Salary Attachments
    # This keeps the contract model clean and uses standard Odoo workflows