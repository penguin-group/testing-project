import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def check_migration_to_secondary_currency_module(self):
        _logger.info("Checking migration to secondary currency module...")
        for company in self.env['res.company'].sudo().search([]):
            try:
                _logger.info(f"Checking balance migration for company: {company.name}...")
                query = """
                    SELECT id, name, balance, balance_ms, secondary_balance 
                    FROM account_move_line
                    WHERE balance_ms != secondary_balance 
                    AND company_id = %s
                """
                parameters = (company.id,)
                self.env.cr.execute(query, parameters)
                rows = self.env.cr.fetchall()
                if rows:
                    _logger.info("The following journal items have differences: ")
                    for r in rows:
                        _logger.info(f"id: {r[0]}, name: {r[1]}, balance_ms: {r[3]}, secondary_balance: {r[4]}")
                else:
                    _logger.info("The journal items have no differences between balance_ms and secondary_balance")
            except Exception as e:
                _logger.error("Error while checking migration data: " + str(e))
                self.env.cr.rollback()

    def compute_secondary_currency_data(self):
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
