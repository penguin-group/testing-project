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




_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    inventory_book_base_report_bs = fields.Many2one(
        'account.report',
        string='Base Report for Balance Sheet',
    )
    inventory_book_base_report_is = fields.Many2one(
        'account.report',
        string='Base Report for Income Statement',
    )
    show_inventory_book_base_report_bs_details = fields.Boolean(
        string='Show Account Details',
        default=True
    )

    def in_paraguay(self):
        py_menu_ext_ids = [
            'l10n_py.book_registration_report_menu',
            'l10n_py.book_registration_menu',
            'l10n_py.invoice_authorization_menu',
            'l10n_py.report_res90_menu',
            'l10n_py.report_vat_purchase_wizard_menu',
            'l10n_py.report_vat_sale_wizard_menu',
        ]
        py_menu_ids = self.env['ir.ui.menu'].browse([self.env.ref(py_menu_ext_id).id for py_menu_ext_id in py_menu_ext_ids])
        in_paraguay = self.env.company.country_code == 'PY'
        if in_paraguay:
            py_menu_ids.sudo().write({
                'show': True,
            })
        else:
            py_menu_ids.sudo().write({
            'show': False,
            })
        return in_paraguay


    '''
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
    '''


    currency_provider = fields.Selection(
        selection_add=[('bcp_closure', 'BCP')],
        string="Currency Provider"
    )

    def _parse_bcp_closure_data(self, available_currencies):
        """Fetch and parse the daily exchange rate from BCP for companies with USD and PYG currencies."""
        _logger.info("Executing _parse_bcp_closure_data")
        result = {}
        currency_names = available_currencies.mapped('name')
        query_date = datetime.now() - timedelta(days=1)
        bcp_request_date = query_date.strftime('%d/%m/%Y')
        rate_application_date = datetime.now().date()

        # Check if the company has a currency provider set to BCP
        try:
            url = self.env['ir.config_parameter'].sudo().get_param('bcp.exchange.url')
            payload = {'fecha': bcp_request_date}
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/x-www-form-urlencoded',
            }

            response = requests.post(url, data=payload, headers=headers, timeout=15)
            _logger.info("BCP Response status: %s", response.status_code)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            table = soup.find('table', class_='table')
            if not table:
                raise ValueError("Exchange table not found in BCP response.")

            thead = table.find('thead')
            if thead:
                header_cells = thead.find_all('th')
                if not any('Compra' in h.get_text() for h in header_cells) or not any('Venta' in h.get_text() for h in header_cells):
                    _logger.warning("Table <thead> headers do not contain expected 'Compra' and 'Venta'. Proceeding with caution.")
            else:
                _logger.warning("Table <thead> not found. Skipping header validation.")

            closing_row = None
            tfoot = table.find('tfoot')
            if tfoot:
                closing_row = tfoot.find('tr')
                _logger.info("<tfoot> found with closing data.")
            else:
                _logger.warning("<tfoot> not found. Using fallback last valid <tbody> row.")
                tbody = table.find('tbody')
                rows = tbody.find_all('tr') if tbody else []
                for row in reversed(rows):
                    cols = row.find_all('td')
                    if len(cols) >= 3 and cols[1].text.strip() and cols[2].text.strip():
                        closing_row = row
                        break

            if not closing_row:
                raise ValueError("Closing row not found in BCP table.")

            # Extract the buying and selling rates from the closing row
            cols = closing_row.find_all(['th', 'td'])
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
                        'date': rate_application_date,
                    }
                result['USD'] = {
                    'rate': 1.0,
                    'company_rate': 1.0,
                    'inverse_company_rate': 1.0,
                    'buying_rate': 1.0,
                    'buying_company_rate': 1.0,
                    'buying_inverse_company_rate': 1.0,
                    'date': rate_application_date,
                }

            elif base_currency == 'PYG':
                if 'USD' in currency_names:
                    result['USD'] = {
                        'rate': buying_rate,
                        'company_rate': buying_rate,
                        'inverse_company_rate': round(1 / buying_rate, 10),
                        'buying_rate': selling_rate,
                        'buying_company_rate': selling_rate,
                        'buying_inverse_company_rate': round(1 / selling_rate, 10),
                        'date': rate_application_date,
                    }
                result['PYG'] = {
                    'rate': 1.0,
                    'company_rate': 1.0,
                    'inverse_company_rate': 1.0,
                    'buying_rate': 1.0,
                    'buying_company_rate': 1.0,
                    'buying_inverse_company_rate': 1.0,
                    'date': rate_application_date,
                }
            else:
                _logger.warning("Unsupported base currency: %s", base_currency)
                return {}

            _logger.info("Final result returned to Odoo: %s", result)
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



    def _generate_currency_rates(self, parsed_data):
        """Generate currency rates for the company based on parsed data from BCP."""
        Currency = self.env['res.currency']
        CurrencyRate = self.env['res.currency.rate']
        for company in self:

            # Check if the company has a currency provider set to BCP
            try:
                company_currency = company.currency_id.name
                currency_info = parsed_data.get(company_currency)

                if not currency_info:
                    raise UserError(
                        f"Base currency ({company_currency}) is missing from provider response."
                    )

                base_rate = (
                    currency_info[0]
                    if isinstance(currency_info, tuple)
                    else currency_info.get('rate')
                )

                for code, values in parsed_data.items():
                    if isinstance(values, dict):
                        rate = values.get('rate', 1.0)
                        date = values.get('date')
                        buying_company_rate = values.get('buying_company_rate')
                        buying_inverse_company_rate = values.get('buying_inverse_company_rate')
                    else:
                        rate, date = values
                        buying_company_rate = None
                        buying_inverse_company_rate = None

                    final_rate = rate / base_rate if base_rate else rate

                    currency = Currency.search([('name', '=', code)], limit=1)
                    if not currency:
                        continue

                    existing = CurrencyRate.search([
                        ('currency_id', '=', currency.id),
                        ('company_id', '=', company.id),
                        ('name', '=', date),
                    ], limit=1)

                    rate_vals = {
                        'currency_id': currency.id,
                        'company_id': company.id,
                        'name': date,
                        'rate': final_rate,
                    }

                    if buying_company_rate:
                        rate_vals['buying_company_rate'] = buying_company_rate
                    if buying_inverse_company_rate:
                        rate_vals['buying_inverse_company_rate'] = buying_inverse_company_rate

                    if existing:
                        existing.write(rate_vals)
                    else:
                        CurrencyRate.create(rate_vals)

                _logger.info("Extended currency rates generated successfully.")

            except UserError as e:
                _logger.exception("User error during currency rate generation: %s", e)
                raise
            except ValueError as e:
                _logger.exception("Value error during currency rate generation: %s", e)
                raise
            except Exception as e:
                _logger.exception("Unexpected error during currency rate generation: %s", e)
                raise

    def _notify_finance_team_error(self, error, provider="BCP"):
        """Notify the finance team about an error in fetching exchange rates."""

        group = self.env.ref('account.group_account_user', raise_if_not_found=False)
        if not group:
            return

        for user in group.users:
            try:

                template = self.env.ref('l10n_py.bcp_exchange_rate_error_notification_l10n')
                template.sudo().send_mail(template.id, force_send=True)


                if user.partner_id:
                    user.sudo().message_notify(
                        subject=_("Exchange Rate Error Notification"),
                        body=_("An error occurred while updating exchange rates. Please check your email for details."),
                        partner_ids=[user.partner_id.id],
                        model_description=_("Exchange Rate Error"),
                        notif_layout='mail.mail_notification_light'
                    )

            except Exception as notify_err:
                _logger.exception("Failed to notify finance team: %s", notify_err)
