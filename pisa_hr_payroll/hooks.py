# -*- coding: utf-8 -*-

import logging
from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Post-installation hook to configure the payroll journal with appropriate accounts"""
    try:
        # Find the payroll journal
        payroll_journal = env.ref('pisa_hr_payroll.account_journal_payroll_py', raise_if_not_found=False)
        if not payroll_journal:
            _logger.warning("Paraguay payroll journal not found during post-install")
            return

        # Try to find a suitable default account for payroll expenses
        # Common account codes for payroll: 621, 6210, 621000, etc.
        account_codes_to_try = ['621', '6210', '621000', '62100', '5101', '510100']
        
        account = None
        for code in account_codes_to_try:
            account = env['account.account'].search([
                ('code', '=like', f'{code}%'),
                ('account_type', 'in', ['expense', 'expense_direct_cost']),
                ('company_id', '=', payroll_journal.company_id.id)
            ], limit=1)
            if account:
                break
        
        # If no specific payroll account found, try general expense accounts
        if not account:
            account = env['account.account'].search([
                ('account_type', '=', 'expense'),
                ('company_id', '=', payroll_journal.company_id.id)
            ], limit=1)
        
        if account:
            payroll_journal.default_account_id = account.id
            _logger.info(f"Set payroll journal default account to {account.code} - {account.name}")
        else:
            _logger.warning("No suitable default account found for payroll journal")
            
    except Exception as e:
        _logger.error(f"Error in payroll post-install hook: {e}")


def uninstall_hook(env):
    """Clean up when uninstalling the module"""
    try:
        # Remove the payroll journal if it exists
        payroll_journal = env.ref('pisa_hr_payroll.account_journal_payroll_py', raise_if_not_found=False)
        if payroll_journal:
            payroll_journal.active = False
            _logger.info("Deactivated Paraguay payroll journal")
    except Exception as e:
        _logger.error(f"Error in payroll uninstall hook: {e}")