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
        selection_add=[('bcp', '[PY] BCP')],
        string="Currency Provider"
    )


    def _parse_bcp_data(self, available_currencies):
        _logger.info("Executing _parse_bcp_data for l10n_py")

        result = {}
        currency_names = available_currencies.mapped('name')

        try:
            url = self.env['ir.config_parameter'].sudo().get_param('bcp.exchange.url')
            headers = {
                "User-Agent": "Mozilla/5.0",
                'Content-Type': 'application/x-www-form-urlencoded',
            }

            # Always post with yesterday's date
            today = fields.Date.context_today(self)
            yesterday = today - timedelta(days=1)
            formatted_yesterday = yesterday.strftime('%Y-%m-%d')

            scraper = cloudscraper.create_scraper()
            response = scraper.post(url, data={'fecha': formatted_yesterday}, headers=headers, timeout=15)
            _logger.info("BCP Response status: %s", response.status_code)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', class_='table')
            if not table:
                raise ValueError("Exchange table not found in BCP response")

            tfoot = table.find('tfoot')
            closing_row = tfoot.find('tr') if tfoot else None
            if not closing_row:
                raise ValueError("Closing row not found in BCP response")

            cols = closing_row.find_all(['td', 'th'])
            if len(cols) < 3:
                raise ValueError("Incomplete closing row found")

            # Extract and validate the actual published date
            closing_label = cols[0].get_text(strip=True)  # e.g. "Cierre 03/06"
            try:
                closing_str = closing_label.split()[-1]
                actual_date = datetime.strptime(closing_str + f'/{datetime.today().year}', '%d/%m/%Y').date()
            except Exception as e:
                raise ValueError(f"Could not parse closing date from label: '{closing_label}'")

            if actual_date != yesterday:
                raise ValueError(f"Expected exchange rate for {yesterday}, but found closing date {actual_date}")

            # Parse exchange values
            buying_rate = float(cols[1].get_text(strip=True).replace('.', '').replace(',', '.'))
            selling_rate = float(cols[2].get_text(strip=True).replace('.', '').replace(',', '.'))

            _logger.info("📅 Valid exchange date confirmed: %s", actual_date)

            if buying_rate <= 0 or selling_rate <= 0:
                raise ValueError("Invalid exchange rate values")

            base_currency = self.currency_id.name
            if base_currency != 'PYG':
                _logger.warning("Base currency %s is not PYG. Skipping.", base_currency)
                return {}

            if 'USD' in currency_names:
                result['USD'] = {
                    'rate': round(1 / buying_rate, 10),
                    'company_rate': round(1 / buying_rate, 10),
                    'inverse_company_rate': buying_rate,
                    'buying_rate': round(1 / selling_rate, 10),
                    'buying_company_rate': round(1 / selling_rate, 10),
                    'buying_inverse_company_rate': selling_rate,
                    'date': actual_date,
                }

            result['PYG'] = {
                'rate': 1.0,
                'company_rate': 1.0,
                'inverse_company_rate': 1.0,
                'buying_rate': 1.0,
                'buying_company_rate': 1.0,
                'buying_inverse_company_rate': 1.0,
                'date': actual_date,
            }

            _logger.info("✅ Final parsed exchange data: %s", result)
            return result

        except Exception as e:
            _logger.exception("Error parsing BCP rates: %s", e)
            return {}




    def _generate_currency_rates(self, parsed_data):
        """Generate currency rates for the company based on parsed data from BCP."""
        Currency = self.env['res.currency']
        CurrencyRate = self.env['res.currency.rate']
        
        if not parsed_data:
            _logger.warning("Parsed data is empty. Skipping currency rate generation.")
            return

        for company in self:
            try:
                company_currency_code = company.currency_id.name
                company_currency_info = parsed_data.get(company_currency_code)

                if not company_currency_info:
                    raise UserError(
                        f"Base currency ({company_currency_code}) is missing from provider response."
                    )

                base_rate = company_currency_info.get('rate', 1.0)

                for code, values in parsed_data.items():
                    currency = Currency.search([('name', '=', code)], limit=1)
                    if not currency:
                        continue

                    raw_rate = values.get('rate', 1.0)
                    date = values.get('date')

                    if code == company_currency_code:
                        final_rate = 1.0
                    else:
                        final_rate = raw_rate / base_rate if base_rate else raw_rate

                    rate_vals = {
                        'currency_id': currency.id,
                        'company_id': company.id,
                        'name': date,
                        'rate': final_rate,
                    }

                    buying_company_rate = values.get('buying_company_rate')
                    buying_inverse_company_rate = values.get('buying_inverse_company_rate')

                    if buying_company_rate:
                        rate_vals['buying_company_rate'] = buying_company_rate
                    if buying_inverse_company_rate:
                        rate_vals['buying_inverse_company_rate'] = buying_inverse_company_rate

                    existing = CurrencyRate.search([
                        ('currency_id', '=', currency.id),
                        ('company_id', '=', company.id),
                        ('name', '=', date),
                    ], limit=1)

                    if existing:
                        existing.write(rate_vals)
                    else:
                        CurrencyRate.create(rate_vals)

                _logger.info("Currency rates generated successfully for company %s.", company.name)
                _logger.warning("Parsed data dict at generate: %s", parsed_data)

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
                    user.partner_id.sudo().message_notify(
                        subject=_("Exchange Rate Error Notification"),
                        body=_("An error occurred while updating exchange rates. Please check your email for details."),
                        partner_ids=[user.partner_id.id],
                        model_description=_("Exchange Rate Error")
                    )

            except Exception as notify_err:
                _logger.exception("Failed to notify finance team: %s", notify_err)
