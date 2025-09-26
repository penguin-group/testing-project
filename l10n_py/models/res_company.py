# -*- coding: utf-8 -*-
from odoo.tools.translate import _
from odoo import models, fields, api, release
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
from odoo import fields, models, tools
from odoo.exceptions import UserError
from odoo.tools.translate import _
import cloudscraper


_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    inventory_book_base_report_bs = fields.Many2one(
        "account.report",
        string="Base Report for Balance Sheet",
    )
    inventory_book_base_report_is = fields.Many2one(
        "account.report",
        string="Base Report for Income Statement",
    )
    show_inventory_book_base_report_bs_details = fields.Boolean(
        string="Show Account Details", default=True
    )

    def in_paraguay(self):
        py_menu_ext_ids = [
            "l10n_py.book_registration_report_menu",
            "l10n_py.book_registration_menu",
            "l10n_py.invoice_authorization_menu",
            "l10n_py.report_res90_menu",
            "l10n_py.report_vat_purchase_wizard_menu",
            "l10n_py.report_vat_sale_wizard_menu",
        ]
        py_menu_ids = self.env["ir.ui.menu"].browse(
            [self.env.ref(py_menu_ext_id).id for py_menu_ext_id in py_menu_ext_ids]
        )
        in_paraguay = self.env.company.country_code == "PY"
        if in_paraguay:
            py_menu_ids.sudo().write(
                {
                    "show": True,
                }
            )
        else:
            py_menu_ids.sudo().write(
                {
                    "show": False,
                }
            )
        return in_paraguay

    """
    This code extends the native currency rate automation in Odoo 
    by integrating the Central Bank of Paraguay (BCP) as a currency provider. 
    It automatically fetches the exchange rates (buy/sell) from the BCP website, 
    parses the required data, and stores the values into extended fields 
    (such as buying_company_rate and buying_inverse_company_rate) 
    for financial automation purposes.

    Key features:
    - Supports PYG as main or secondary currency
    - Automatically populates both selling and buying rates
    - Notifies the finance team on failure via popup and email
    """

    currency_provider = fields.Selection(
        selection_add=[("bcp", "[PY] BCP")], string="Currency Provider"
    )

    def _parse_bcp_data(self, available_currencies):
        """Base BCP parser implementation."""
        _logger.info("Executing _parse_bcp_data")

        result = {}
        currency_names = available_currencies.mapped("name")
        base_currency = self.currency_id.name

        if base_currency not in ["USD", "PYG"]:
            _logger.warning(
                "Base currency %s not supported for BCP parser.", base_currency
            )
            return {}

        try:
            exchange_data = self._fetch_bcp_exchange_data()
            if not exchange_data:
                return {}

            return self._process_exchange_data(
                exchange_data, currency_names, base_currency
            )

        except Exception as e:
            _logger.exception("Error in BCP parser: %s", e)
            self._notify_finance_team_error(e, provider="BCP")
            return {}

    def _fetch_bcp_exchange_data(self):
        """Fetch exchange data from BCP."""
        today = fields.Date.context_today(self)
        yesterday = today - timedelta(days=1)
        formatted_yesterday = yesterday.strftime("%Y-%m-%d")

        url = self.env["ir.config_parameter"].sudo().get_param("bcp.exchange.url")
        headers = self._get_bcp_headers()

        scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "darwin", "mobile": False},
            delay=10,
        )

        response = scraper.post(
            url, data={"fecha": formatted_yesterday}, headers=headers, timeout=30
        )
        _logger.info("BCP Response status: %s", response.status_code)
        response.raise_for_status()

        return self._parse_bcp_response(response, yesterday)

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
            raise ValueError("Exchange table not found in BCP response")

        closing_row = self._find_closing_row(table)
        if not closing_row:
            raise ValueError("No valid closing row found")

        actual_date = self._validate_exchange_date(closing_row, expected_date)
        buying_rate, selling_rate = self._extract_rates(closing_row)

        return {
            "date": actual_date,
            "buying_rate": buying_rate,
            "selling_rate": selling_rate,
        }

    def _process_exchange_data(self, exchange_data, currency_names, base_currency):
        """Process exchange data based on base currency."""
        result = {}

        if base_currency == "USD":
            result = self._process_usd_based(exchange_data, currency_names)
        elif base_currency == "PYG":
            result = self._process_pyg_based(exchange_data, currency_names)

        _logger.info("Final parsed exchange data: %s", result)
        return result

    def _process_usd_based(self, exchange_data, currency_names):
        """Process exchange data for USD-based companies."""
        Currency = self.env["res.currency"].sudo()
        CurrencyRate = self.env["res.currency.rate"].sudo()

        result = {}
        if "PYG" in currency_names:
            currency = Currency.search([("name", "=", "PYG")], limit=1)
            if currency:
                CurrencyRate.create(
                    {
                        "currency_id": currency.id,
                        "company_id": self.id,
                        "name": exchange_data["date"],
                        "company_rate": exchange_data["selling_rate"],
                        "buying_company_rate": exchange_data["buying_rate"],
                    }
                )
        return result

    def _process_pyg_based(self, exchange_data, currency_names):
        """Process exchange data for PYG-based companies."""
        Currency = self.env["res.currency"].sudo()
        CurrencyRate = self.env["res.currency.rate"].sudo()

        result = {}
        if "USD" in currency_names:
            currency = Currency.search([("name", "=", "USD")], limit=1)
            if currency:
                CurrencyRate.create(
                    {
                        "currency_id": currency.id,
                        "company_id": self.id,
                        "name": exchange_data["date"],
                        "inverse_company_rate": exchange_data["selling_rate"],
                        "buying_inverse_company_rate": exchange_data["buying_rate"],
                    }
                )
        return result

    def _notify_finance_team_error(self, error, provider="BCP"):
        """Notify the finance team about an error in fetching exchange rates."""

        group = self.env.ref("account.group_account_user", raise_if_not_found=False)
        if not group:
            return

        for user in group.users:
            try:

                template = self.env.ref(
                    "l10n_py.bcp_exchange_rate_error_notification_l10"
                )
                template.with_context(
                    provider=provider,
                    error=error,
                ).sudo().send_mail(self.id, force_send=True)

                if user.partner_id:
                    user.partner_id.sudo().message_notify(
                        subject=("Exchange Rate Error Notification"),
                        body=(
                            "An error occurred while updating exchange rates. Please check your email for details."
                        ),
                        partner_ids=[user.partner_id.id],
                        model_description=("Exchange Rate Error"),
                    )

            except Exception as notify_err:
                _logger.exception("Failed to notify finance team: %s", notify_err)

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
                cells = row.find_all("td")
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
            _logger.error("Error finding closing row: %s", str(e))
            return None

    def _validate_exchange_date(self, row, expected_date):
        """Validate and parse the exchange rate date from row.

        Args:
            row: BeautifulSoup row element
            expected_date: datetime.date object of expected date

        Returns:
            datetime.date object of actual exchange rate date

        Raises:
            ValueError if the actual date does not match the expected date.
        """
        try:
            date_cell = row.find("td")
            if not date_cell:
                raise ValueError("Date cell is missing.")

            date_text = date_cell.get_text().strip()
            actual_date = datetime.strptime(date_text, "%d/%m/%Y").date()

            # Check for exact match
            if actual_date != expected_date:
                raise ValueError(
                    "Exchange rate date (%s) does not match expected date (%s)",
                    actual_date,
                    expected_date,
                )

            return actual_date

        except Exception as e:
            _logger.error("Error parsing date: %s. Using expected date.", str(e))
            return expected_date

    def _extract_rates(self, row):
        """Extract buying and selling rates from row.

        Args:
            row: BeautifulSoup row element

        Returns:
            tuple(float, float) - (buying_rate, selling_rate)
        """
        cells = row.find_all("td")
        if len(cells) < 3:
            raise ValueError("Row does not contain enough cells for rates")

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
            raise ValueError(f"Failed to parse rates from row: {str(e)}")
