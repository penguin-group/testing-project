import logging
from odoo import models, fields, api
from itertools import islice


_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'        

    def migrate_secondary_currency_data(self):
        result = []

        _logger.info(f"MIGRATING COMPANY DATA")

        try:
            _logger.info("Migrating company secondary currency")
            self.env.cr.execute("""
                UPDATE res_company
                SET
                    sec_currency_id = secondary_currency_id
            """)
            result.append(True)
        except Exception as e:
            _logger.error("Error while migrating secondary currency: " + str(e))
            self.env.cr.rollback() 
            result.append(False)

        for company in self.env['res.company'].sudo().search([]):

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

    def compute_sec_currency_rates_with_zero_vals(self):
        records = self.search([('invoice_secondary_currency_rate', '=', False), ('state', 'not in', ['draft'])])
        index = 0
        records_count = len(records)
        for record in records:
            index += 1
            record._compute_invoice_secondary_currency_rate()
            percentage_complete = index / records_count * 100
            _logger.info(f'Processing {record.name}... {percentage_complete:.2f}% complete')
            
            