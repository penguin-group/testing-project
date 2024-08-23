from odoo import _, api, fields, models

import logging
_logger = logging.getLogger(__name__)

class ConsolidationCoa(models.Model):
    _inherit = 'consolidation.account'

    account_prefix = fields.Char(
        'Account Prefixes', 
        help="Account prefixes to include autommaticaly in this consolidation account. Separated by commas."
    )

    def check_consolidated_accounts(self):
        consolidated_accounts = self.search([])
        for account in consolidated_accounts:
            if account.account_prefix:
                try:
                    prefixes = account.account_prefix.split(',')
                    for prefix in prefixes:
                        matching_accounts = self.env['account.account'].search([
                            ('code', '=like', prefix + '%'),
                            ('company_id', 'in', account.company_ids.mapped('id'))
                        ])
                        accounts_to_add = matching_accounts - account.account_ids
                        if accounts_to_add:
                            account.write({'account_ids': [(4, acc.id) for acc in accounts_to_add]})
                except Exception as error:
                    _logger.error(f'Error checking consolidated accounts: {str(error)}')