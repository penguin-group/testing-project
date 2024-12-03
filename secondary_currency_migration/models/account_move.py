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

            _logger.info(f"Migrating data of the journal entries for: {company.name}...")
            
            try:
                _logger.info("Migrating freezed secondary currency rates...")
                self.env.cr.execute("""
                    UPDATE account_move am
                    SET
                        invoice_secondary_currency_rate = 
                            CASE WHEN am.currency_rate != 0 THEN 
                                CASE WHEN cur.name = 'PYG' THEN
                                    am.currency_rate
                                ELSE
                                    1 / am.currency_rate
                                END
                            ELSE 
                                0
                            END
                    FROM res_company c
                    JOIN res_currency cur ON c.currency_id = cur.id
                    WHERE am.company_id = c.id
                    AND c.id = %s
                    AND am.freeze_currency_rate = true;
                """, (company.id,))
                result.append(True)
            except Exception as e:
                _logger.error("Error while migrating currency rates: " + str(e))
                self.env.cr.rollback() 
                result.append(False)

            try:
                _logger.info("Migrating secondary currency rates of the remaining journal entries...")
                self.compute_sec_currency_rates_with_zero_vals(company)
                result.append(True)
            except Exception as e:    
                _logger.error("Error while migrating currency rates of remaining journal entries: " + str(e))
                self.env.cr.rollback() 
                result.append(False)
            
            try:
                _logger.info("Migrating secondary balances according to previous balance ms...")
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
        
        
        try:
            _logger.info("Migrating secondary balances of the remaining journal entries...")
            query = """
                UPDATE account_move_line
                SET secondary_balance = (
                    CASE
                        WHEN aml.display_type IN ('line_section', 'line_note') THEN 0
                        WHEN aml.currency_id = secondary_currency.id THEN ROUND(aml.amount_currency, secondary_currency.decimal_places)
                        ELSE ROUND(aml.balance / am.invoice_secondary_currency_rate, secondary_currency.decimal_places)
                    END
                )
                FROM account_move_line aml
                JOIN account_move am ON am.id = aml.move_id
                JOIN res_company company ON company.id = am.company_id
                JOIN res_currency secondary_currency ON secondary_currency.id = company.sec_currency_id
                WHERE aml.id = account_move_line.id
                AND am.state NOT IN ('posted')
            """
            self.env.cr.execute(query)
            result.append(True)
        except Exception as e:
            _logger.error("Migrating secondary balances of the remaining journal entries: " + str(e))
            self.env.cr.rollback() 
            result.append(False)
        
        
        if all(result):
            _logger.info("Migration completed successfully.")
        
        else:
            _logger.error("There was an error during the migration. Check the logs for more information.")

    def compute_sec_currency_rates_with_zero_vals(self, company):
        records = self.sudo().search([('freeze_currency_rate', '=', False), ('company_id', '=', company.id)])
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
        except Exception as e:
            _logger.error(f"Error while computing secondary currency rate for account move {self.name}: {str(e)}")


            
            