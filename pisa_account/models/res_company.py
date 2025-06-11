from datetime import datetime, timedelta
import logging
import requests
from bs4 import BeautifulSoup
from odoo.tools.translate import _
import cloudscraper 


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

from datetime import datetime, timedelta
import logging
import requests
from bs4 import BeautifulSoup
from odoo.tools.translate import _
import cloudscraper
from odoo import models, fields

_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
    _inherit = 'res.company'

    def _parse_bcp_data(self, available_currencies):
        """Fetch and parse the daily exchange rate from BCP for companies where USD is the base and PYG is secondary."""
        _logger.info("Executing _parse_bcp_data for pisa_account")

        if self.currency_id.name != 'USD':
            _logger.warning("Skipping pisa_account parser. Company base currency is not USD. Delegating to l10n_py via super().")
            return super()._parse_bcp_data(available_currencies)

        result = {}
        currency_names = available_currencies.mapped('name')

        # Always post with yesterday's date
        today = fields.Date.context_today(self)
        yesterday = today - timedelta(days=1)
        formatted_yesterday = yesterday.strftime('%Y-%m-%d')

        try:
            url = self.env['ir.config_parameter'].sudo().get_param('bcp.exchange.url')
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                'Content-Type': 'application/x-www-form-urlencoded',
            }

            payload = {'fecha': formatted_yesterday}
            scraper = cloudscraper.create_scraper()
            response = scraper.post(url, data=payload, headers=headers, timeout=15)
            _logger.info("BCP Response status: %s", response.status_code)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', class_='table')
            if not table:
                raise ValueError("Exchange table not found in BCP response.")

            closing_row = None
            tfoot = table.find('tfoot')
            if tfoot:
                closing_row = tfoot.find('tr')
                _logger.info("Found closing row in <tfoot>.")
            else:
                _logger.warning("<tfoot> not found. Looking into <tbody> for valid data...")
                tbody = table.find('tbody')
                rows = tbody.find_all('tr') if tbody else []
                for row in reversed(rows):
                    cols = row.find_all('td')
                    if len(cols) >= 3 and cols[1].text.strip() and cols[2].text.strip():
                        closing_row = row
                        _logger.info("Found valid fallback row in <tbody>: %s", row)
                        break

            if not closing_row:
                raise ValueError("No valid closing row found in either <tfoot> or <tbody>.")

            cols = closing_row.find_all(['th', 'td'])
            if len(cols) < 3:
                raise ValueError("Incomplete closing row found")

            # Extract and validate actual published date
            closing_label = cols[0].get_text(strip=True)  # e.g. "Cierre 03/06"
            try:
                closing_str = closing_label.split()[-1]
                actual_date = datetime.strptime(closing_str + f'/{datetime.today().year}', '%d/%m/%Y').date()
            except Exception as e:
                raise ValueError(f"Could not parse closing date from label: '{closing_label}'")

            if actual_date != yesterday:
                raise ValueError(f"Expected exchange rate for {yesterday}, but found closing date {actual_date}")

            # Parse values
            buying_rate = float(cols[1].get_text(strip=True).replace('.', '').replace(',', '.'))
            selling_rate = float(cols[2].get_text(strip=True).replace('.', '').replace(',', '.'))

            if buying_rate <= 0 or selling_rate <= 0:
                _logger.warning("Invalid rate: Buy %s, Sell %s", buying_rate, selling_rate)
                return {}

            base_currency = self.currency_id.name
            _logger.info("Company base currency: %s", base_currency)

            if base_currency == 'USD':
                if 'PYG' in currency_names:
                    result['PYG'] = {
                        'rate': selling_rate,
                        'company_rate': selling_rate,
                        'inverse_company_rate': round(1 / selling_rate, 10),
                        'buying_rate': buying_rate,
                        'buying_company_rate': buying_rate,
                        'buying_inverse_company_rate': round(1 / buying_rate, 10),
                        'date': actual_date,  # ✅ fixed here
                    }
                result['USD'] = {
                    'rate': 1.0,
                    'company_rate': 1.0,
                    'inverse_company_rate': 1.0,
                    'buying_rate': 1.0,
                    'buying_company_rate': 1.0,
                    'buying_inverse_company_rate': 1.0,
                    'date': actual_date,  # ✅ and here
                }
            else:
                _logger.warning("Base currency %s not supported for pisa_account.", base_currency)
                return {}

            _logger.info("Final parsed exchange data: %s", result)
            return result

        except requests.exceptions.RequestException as e:
            _logger.exception("HTTP error fetching BCP rates: %s", e)
            self._notify_finance_team_error(e, provider="BCP")
        except ValueError as e:
            _logger.exception("Value error parsing BCP response: %s", e)
            self._notify_finance_team_error(e, provider="BCP")
        except Exception as e:
            _logger.exception("Unexpected error in BCP rate parser: %s", e)
            self._notify_finance_team_error(e, provider="BCP")

        return {}





    def _notify_finance_team_error(self, error, provider="BCP"):
        """Notify the finance team about an error in fetching exchange rates."""

        group = self.env.ref('account.group_account_user', raise_if_not_found=False)
        if not group:
            return

        for user in group.users:
            try:

                template = self.env.ref('l10n_py.bcp_exchange_rate_error_notification_l10n')
                template.with_context(
                    provider=provider,
                    error=error,
                ).sudo().send_mail(self.id, force_send=True)


                if user.partner_id:
                    user.partner_id.sudo().message_notify(
                    subject=("Exchange Rate Error Notification"),
                    body=("An error occurred while updating exchange rates. Please check your email for details."),
                    partner_ids=[user.partner_id.id],
                    model_description=("Exchange Rate Error")
)

            except Exception as notify_err:
                _logger.exception("Failed to notify finance team: %s", notify_err)
