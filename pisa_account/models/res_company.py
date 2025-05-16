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
        _logger.info("Executing _parse_bcp_data for pisa_account")
        result = {}
        currency_names = available_currencies.mapped('name')
        query_date = datetime.now() - timedelta(days=1)
        bcp_request_date = query_date.strftime('%d/%m/%Y')
        today_date = datetime.now().date()

        try:
            url = self.env['ir.config_parameter'].sudo().get_param('bcp.exchange.url.pisa')
            if not url:
                raise ValueError("BCP exchange URL not configured in system parameters.")

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

            tfoot = table.find('tfoot')
            closing_row = tfoot.find('tr') if tfoot else None
            if not closing_row:
                raise ValueError("No valid closing row found. Only <tfoot> rates are accepted.")

            cols = closing_row.find_all(['th', 'td'])
            buying = float(cols[1].get_text(strip=True).replace('.', '').replace(',', '.'))
            sale = float(cols[2].get_text(strip=True).replace('.', '').replace(',', '.'))

            if buying <= 0 or sale <= 0:
                raise ValueError(f"Invalid exchange rates: buy={buying}, sell={sale}")

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
                _logger.warning("Base currency %s not supported for pisa_account.", base_currency)
                return {}

            _logger.info("Final exchange data sent to Odoo: %s", result)
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
        try:
            group = self.env.ref('account.group_account_user', raise_if_not_found=False)
            if not group:
                return

            for user in group.users:
                subject = ("Error in exchange rate update (%s)") % provider
                body_html = (
                    "<p><strong>Automatically generated error</strong></p>"
                    "<p><strong>Provider:</strong> %s</p>"
                    "<p><strong>Error:</strong> %s</p>"
                ) % (provider, error)

                template = self.env.ref('pisa_account.bcp_exchange_rate_error_notification_pisa')
                template.with_context(
                    provider=provider,
                    error=error,
                ).sudo().send_mail(self.id, force_send=True)

                if user.partner_id:
                    user.sudo().message_notify(
                        subject=subject,
                        body=body_html,
                        partner_ids=[user.partner_id.id],
                        model_description=subject,
                        notif_layout='mail.mail_notification_light'
                    )
        except Exception as notify_error:
            _logger.exception("Error while notifying finance team: %s", notify_error)
