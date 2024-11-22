import logging
from odoo import models, fields, api
from itertools import islice


_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'        

    def migrate_secondary_currency_data(self):
        result = []
        for company in self.env['res.company'].sudo().search([]):
            _logger.info(f"MIGRATING DATA OF THE COMPANY: {company.name}")
            _logger.info("Migrating company secondary currency data...")

            try:
                company.sudo().write({
                    'sec_currency_id': company.secondary_currency_id.id if company.secondary_currency_id else self.env.ref('base.PYG').id,
                })
                _logger.info(f"Secondary Currency set to {company.secondary_currency_id.name}.")
            except Exception as e:
                _logger.error("Error while migrating company secondary currency data: " + str(e))
                self.env.cr.rollback() 
                result.append(False)                

            _logger.info("Migrating data of the journal entries...")
            
            try:
                _logger.info("Migrating currency rates...")
                self.env.cr.execute("""
                    UPDATE account_move
                    SET
                        invoice_secondary_currency_rate = currency_rate
                    WHERE company_id = %s and freeze_currency_rate = true
                """, (company.id,))
                result.append(True)
            except Exception as e:
                _logger.error("Error while migrating currency rates: " + str(e))
                self.env.cr.rollback() 
                result.append(False)
            
            
            try:
                _logger.info("Migrating balance...invoice_secondary_currency_rate")
                self.env.cr.execute("""
                    UPDATE account_move_line
                    SET
                        secondary_balance = balance_ms
                    WHERE company_id = %s
                """, (
                    company.id,
                ))
                result.append(True)
            except Exception as e:
                _logger.error("Error while migrating balance: " + str(e))
                self.env.cr.rollback() 
                result.append(False)


        if all(result):
            _logger.info("Migration completed successfully.")
        else:
            _logger.error("There was an error during the migration. Check the logs for more information.")