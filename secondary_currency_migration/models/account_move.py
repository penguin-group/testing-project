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
        records = self.search([('freeze_currency_rate', '=', False)])
        index = 0
        records_count = len(records)
        for record in records:
            index += 1
            record.compute_sec_currency_rate_sql()
            percentage_complete = index / records_count * 100
            _logger.info(f'{percentage_complete:.2f}% complete')

    def compute_sec_currency_rate_sql(self):
        self.ensure_one()
        if not self.company_id.sec_currency_id:
            _logger.warning(f"No secondary currency set for company {self.company_id.name}")
            return

        try:
            query = """
                        UPDATE account_move am
                        SET invoice_secondary_currency_rate = (
                            SELECT 1 / rcr.rate 
                            FROM res_currency_rate rcr
                            WHERE rcr.currency_id = %s
                              AND rcr.name <= %s
                              AND rcr.company_id = %s
                            ORDER BY rcr.name DESC
                            LIMIT 1
                        )
                        WHERE am.id = %s;
                    """
            self.env.cr.execute(query, (self.company_id.sec_currency_id.id, self.date, self.company_id.id, self.id))
            _logger.info(f"Successfully computed secondary currency rate for account move {self.name}")
        except Exception as e:
            _logger.error(f"Error while computing secondary currency rate for account move {self.name}: {str(e)}")


            
            