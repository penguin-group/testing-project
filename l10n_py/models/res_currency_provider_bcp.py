from odoo import models, fields, _
from bs4 import BeautifulSoup
import cloudscraper
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ResCurrencyProviderBCP(models.AbstractModel):
    _name = "res.currency.provider.bcp"
    _description = "BCP Exchange Rate Provider"

    """Central Bank of Paraguay (BCP) Currency Rate Provider.

    This model provides integration with BCP's exchange rate service, fetching
    daily rates for USD/PYG currency pairs. It extends Odoo's currency rate
    automation system to support Paraguay's specific requirements.

    Technical Details:
        - Fetches rates from BCP's official website
        - Uses web scraping with cloudscraper to handle JavaScript rendering
        - Supports both USD and PYG as base currencies
        - Handles both buying and selling rates
        - Integrates with Odoo's currency rate scheduling system

    Features:
        - Automatic daily rate updates
        - Dual rate support (buying/selling)
        - Error notification system for finance team
        - Historical rate lookup
        - Rate validation and verification

    Fields Extended:
        - company_rate: Selling rate when USD is base
        - inverse_company_rate: Selling rate when PYG is base
        - buying_company_rate: Buying rate when USD is base
        - buying_inverse_company_rate: Buying rate when PYG is base

    Usage:
        The provider is automatically used when selected in the company's
        currency configuration with 'BCP' as the provider.
    """

    def fetch_rates(self, date, available_currencies, base_currency):
        """Fetch BCP rates for the given date.

        Args:
            date: datetime.date object - The date to fetch rates for
            available_currencies: recordset of currencies
            base_currency: string - Base currency code ('USD' or 'PYG')

        Returns:
            dict: Currency rates in the format:
                {
                    'USD': {
                        'date': date,
                        'selling_rate': float,
                        'buying_rate': float
                    },
                    'PYG': {
                        'date': date,
                        'selling_rate': float,
                        'buying_rate': float
                    }
                }
        """
        try:
            exchange_data = self._fetch_bcp_exchange_data(date)
            if not exchange_data:
                return {}

            currency_names = available_currencies.mapped("name")
            result = {}

            # Add rates based on base currency
            if base_currency == "USD" and "PYG" in currency_names:
                result["PYG"] = {
                    "date": exchange_data["date"],
                    "selling_rate": exchange_data["selling_rate"],
                    "buying_rate": exchange_data["buying_rate"],
                }
            elif base_currency == "PYG" and "USD" in currency_names:
                result["USD"] = {
                    "date": exchange_data["date"],
                    "selling_rate": exchange_data["selling_rate"],
                    "buying_rate": exchange_data["buying_rate"],
                }

            _logger.info(_("Final BCP rates: %s"), result)
            return result

        except Exception as e:
            _logger.exception(_("Error fetching BCP rates: %s"), e)
            return {}

    def _fetch_bcp_exchange_data(self, date):
        """Fetch exchange data from BCP."""
        formatted_date = date.strftime("%Y-%m-%d")

        url = self.env["ir.config_parameter"].sudo().get_param("bcp.exchange.url")
        headers = self._get_bcp_headers()

        scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "darwin", "mobile": False},
            delay=10,
        )

        response = scraper.post(
            url, data={"fecha": formatted_date}, headers=headers, timeout=30
        )
        _logger.info("BCP Response status: %s", response.status_code)
        response.raise_for_status()

        return self._parse_bcp_response(response, date)

    def _get_bcp_headers(self):
        """Get headers for BCP request."""
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def _parse_bcp_response(self, response, expected_date):
        """Parse BCP response and extract exchange rates."""
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", class_="table")
        if not table:
            raise ValueError(_("Exchange table not found in BCP response"))

        closing_row = self._find_closing_row(table)
        if not closing_row:
            raise ValueError(_("No valid closing row found"))

        actual_date = self._validate_exchange_date(closing_row, expected_date)
        buying_rate, selling_rate = self._extract_rates(closing_row)

        return {
            "date": actual_date,
            "buying_rate": buying_rate,
            "selling_rate": selling_rate,
        }

    def _find_closing_row(self, table):
        """Find the closing exchange rate row in the BCP table.

        Args:
            table: BeautifulSoup table element

        Returns:
            BeautifulSoup row element or None if not found
        """
        try:
            # Look for the last row with numeric values
            rows = table.find_all("tr")
            for row in reversed(rows):
                cells = row.find_all("th")
                if len(cells) >= 3:  # Need at least 3 cells (date, buy, sell)
                    # Check if second and third cells contain numeric values
                    try:
                        float(
                            cells[1]
                            .get_text()
                            .strip()
                            .replace(".", "")
                            .replace(",", ".")
                        )
                        float(
                            cells[2]
                            .get_text()
                            .strip()
                            .replace(".", "")
                            .replace(",", ".")
                        )
                        return row
                    except (ValueError, IndexError):
                        continue
            return None

        except Exception as e:
            _logger.error(_("Error finding closing row: %s"), str(e))
            return None

    def _validate_exchange_date(self, row, expected_date):
        """Validate and parse the exchange rate date from row.

        Args:
            row: BeautifulSoup row element
            expected_date: datetime.date object of expected date

        Returns:
            datetime.date object of actual exchange rate date

        Raises:
            ValueError if the actual date does not match the expected date or if an error occurs.
        """
        try:
            date_cell = row.find("th")
            if not date_cell:
                raise ValueError(_("Date cell is missing."))

            date_text = date_cell.get_text().strip().split()[-1]
            actual_date = datetime.strptime(
                date_text + f"/{datetime.today().year}", "%d/%m/%Y"
            ).date()

            # Check for exact match
            if actual_date != expected_date:
                raise ValueError(
                    _("Exchange rate date (%s) does not match expected date (%s)"),
                    actual_date,
                    expected_date,
                )

            return actual_date

        except Exception as e:
            _logger.error(_("Error parsing date: %s"), str(e))
            raise ValueError(_("Failed to validate exchange date.")) from e

    def _extract_rates(self, row):
        """Extract buying and selling rates from row.

        Args:
            row: BeautifulSoup row element

        Returns:
            tuple(float, float) - (buying_rate, selling_rate)
        """
        cells = row.find_all("th")
        if len(cells) < 3:
            raise ValueError(_("Row does not contain enough cells for rates"))

        try:
            # Convert string rates to float (handle Paraguayan number format)
            buying_text = cells[1].get_text().strip().replace(".", "").replace(",", ".")
            selling_text = (
                cells[2].get_text().strip().replace(".", "").replace(",", ".")
            )

            buying_rate = float(buying_text)
            selling_rate = float(selling_text)

            return buying_rate, selling_rate

        except (ValueError, IndexError) as e:
            raise ValueError(_("Failed to parse rates from row: %s") % str(e))

    def _notify_finance_team_error(self, error, provider="BCP"):
        """Notify the finance team about an error in fetching exchange rates."""
        group = self.env.ref("account.group_account_user", raise_if_not_found=False)
        if not group:
            return

        for user in group.users:
            try:
                if user.partner_id:
                    user.partner_id.sudo().message_notify(
                        subject=_("Exchange Rate Error Notification"),
                        body=_(
                            "An error occurred while updating exchange rates from the %s provider: %s."
                            % (provider, str(error))
                        ),
                        partner_ids=[user.partner_id.id],
                        model_description=_("Exchange Rate Error"),
                    )

            except Exception as notify_err:
                _logger.exception(_("Failed to notify finance team: %s"), notify_err)
