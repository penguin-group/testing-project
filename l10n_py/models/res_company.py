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

    currency_provider = fields.Selection(
        selection_add=[("bcp", "[PY] BCP")], string="Currency Provider"
    )

    def _parse_bcp_data(self, available_currencies):
        """Base BCP parser implementation using BCP Rate Provider.
        Only fetch rates if not already present for the requested date.
        """
        if self.currency_id.name not in ["USD", "PYG"]:
            _logger.warning(
                _("Base currency %s not supported for BCP parser."),
                self.currency_id.name,
            )
            return {}

        bcp_provider = self.env["res.currency.provider.bcp"]
        yesterday = fields.Date.context_today(self) - timedelta(days=1)

        # Check if rates already exist for all requested currencies for yesterday
        CurrencyRate = self.env["res.currency.rate"].sudo()
        rate_exists = False
        for currency in available_currencies.filtered(
            lambda c: c.name in ["USD", "PYG"]
        ):
            rate_exists = CurrencyRate.search_count([
                ("currency_id", "=", currency.id),
                ("name", "=", yesterday),
                ("company_id", "=", self.id),
            ]) > 0
            if rate_exists:
                message = _("Currency rates for %s already exist for %s." % (currency.name, yesterday))
                _logger.info(message)
                raise UserError(message)            

        return bcp_provider.fetch_rates(
            yesterday, available_currencies, self.currency_id.name
        )

    def _generate_currency_rates(self, parsed_data): 
        """Generate currency rate entries for each company based on the parsed data.

        Args:
            parsed_data (dict): Dictionary containing currency rates data in format:
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
        Currency = self.env["res.currency"].sudo()
        CurrencyRate = self.env["res.currency.rate"].sudo()

        for company in self:
            base_currency = company.currency_id.name

            for currency, data in parsed_data.items():
                currency_object = Currency.search([("name", "=", currency)])
                if not currency_object:
                    continue

                rate_vals = {
                    "currency_id": currency_object.id,
                    "name": data["date"],
                    "company_id": company.id,
                }

                # Set rates based on base currency
                if base_currency == "USD":
                    rate_vals.update(
                        {
                            "company_rate": data["selling_rate"],
                            "buying_company_rate": data["buying_rate"],
                        }
                    )
                else:  # PYG
                    rate_vals.update(
                        {
                            "inverse_company_rate": data["selling_rate"],
                            "buying_inverse_company_rate": data["buying_rate"],
                        }
                    )

                CurrencyRate.create(rate_vals)
