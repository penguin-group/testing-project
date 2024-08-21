from odoo import _, api, fields, models

class ConsolidationCoa(models.Model):
    _inherit = 'consolidation.account'

    account_prefix = fields.Char(
        'Account Prefixes', 
        help="Account prefixes to include autommaticaly in this consolidation account. Separated by commas."
    )

    def check_consolidated_accounts(self):
        # Iterate through each consolidated account
        consolidated_accounts = self.search([])
        for account in consolidated_accounts:
            if account.account_prefixes:
                # Get the prefixes
                prefixes = account.account_prefixes.split(',')

                # Search for all accounts that match the prefixes
                for prefix in prefixes:
                    matching_accounts = self.env['account.account'].search([
                        ('code', '=like', prefix + '%')
                    ])

                    # Filter the accounts that are not included in the consolidated account
                    accounts_to_add = matching_accounts - account.account_ids

                    # Add the missing accounts to the consolidated account
                    if accounts_to_add:
                        account.write({'account_ids': [(4, acc.id) for acc in accounts_to_add]})