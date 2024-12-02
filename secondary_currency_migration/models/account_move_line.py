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
        records = self.search([('secondary_balance', '=', False), ('move_id.state', 'not in', ['posted'])])
        index = 0
        records_count = len(records)
        for record in records:
            index += 1
            record._compute_secondary_balance()
            percentage_complete = index / records_count * 100
            _logger.info(f'{percentage_complete:.2f}% | Processing {record.name}...')
