from datetime import datetime, timedelta
import logging
import requests
from bs4 import BeautifulSoup

from odoo import models, fields, tools

_logger = logging.getLogger(__name__)

'''
    This method retrieves and parses the daily exchange rate from the Central Bank of Paraguay (BCP)
    specifically for companies where the base currency is USD and PYG is a secondary currency.
    It returns a dictionary with the formatted exchange rates for Odoo including:
    - 'rate' (sale rate)
    - 'buying_rate' (buy rate)
    - Inverse and company rates.
    If an error occurs, it notifies the finance team and logs the exception.
'''

class ResCompany(models.Model):
    _inherit = 'res.company'

    currency_provider = fields.Selection(
        selection_add=[('bcp', 'BCP')],
        string="Currency Provider"
    )

    def _parse_bcp_data(self, available_currencies):
        '''
        This method is called to parse the BCP data for the company.'''

        _logger.info("Executing _parse_bcp_closure_data for pisa_account")
        result = {}
        currency_names = available_currencies.mapped('name')
        date_post = (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y')
        today_date = datetime.now().date()

        try:
            url = "https://www.bcp.gov.py/webapps/web/cotizacion/referencial-fluctuante"
            payload = {'date': date_post}
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/x-www-form-urlencoded',
            }

            response = requests.post(url, data=payload, headers=headers, timeout=15)
            _logger.info("BCP response status: %s", response.status_code)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', class_='table')

            closure_row = table.find('tfoot').find('tr') if table.find('tfoot') else None

            if not closure_row:
                _logger.warning("<tfoot> not found. Trying <tbody> fallback.")
                for row in reversed(table.find('tbody').find_all('tr')):
                    cols = row.find_all('td')
                    if len(cols) >= 3 and cols[1].text.strip() and cols[2].text.strip():
                        closure_row = row
                        break

            if not closure_row:
                raise ValueError("No valid closing row found.")

            cols = closure_row.find_all(['th', 'td'])
            buying = float(cols[1].get_text(strip=True).replace('.', '').replace(',', '.'))
            sale = float(cols[2].get_text(strip=True).replace('.', '').replace(',', '.'))

            if buying <= 0 or sale <= 0:
                _logger.warning("Invalid exchange values: buying %s, sale %s", buying, sale)
                return {}

            base_currency = self.currency_id.name
            _logger.info("Company base currency: %s", base_currency)

            if base_currency == 'USD':
                if 'PYG' in currency_names:
                    result['PYG'] = {
                        'rate': sale,
                        'company_rate': sale,
                        'inverse_company_rate': round(1 / sale, 10),
                        'buying_rate': buying,
                        'buying_company_rate': buying,
                        'buying_inverse_company_rate': round(1 / buying, 10),
                        'date': today_date,
                    }
                result['USD'] = {
                    'rate': 1.0,
                    'company_rate': 1.0,
                    'inverse_company_rate': 1.0,
                    'buying_rate': 1.0,
                    'buying_company_rate': 1.0,
                    'buying_inverse_company_rate': 1.0,
                    'date': today_date,
                }
            else:
                _logger.warning(" Base currency %s not supported for pisa_account.", base_currency)
                return {}

            _logger.info(" Final exchange data sent to Odoo: %s", result)
            return result

        except Exception as e:
            _logger.exception(" Error retrieving BCP data: %s", e)
            self._notify_finance_team_error(e, provider="BCP")
            return {}
