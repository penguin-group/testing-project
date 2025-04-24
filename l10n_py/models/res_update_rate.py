from odoo import models, fields
from datetime import datetime, timedelta
from decimal import Decimal
import requests
from bs4 import BeautifulSoup
import logging

_logger = logging.getLogger(__name__)

# 💡 Agregamos el proveedor BCP al listado global
try:
    from odoo.addons.account.models import res_company
    res_company.CURRENCY_PROVIDER_SELECTION.append((['PY'], 'bcp_cierre', '[PY] BCP - Cierre'))
except Exception as e:
    _logger.warning("⚠️ No se pudo extender CURRENCY_PROVIDER_SELECTION: %s", e)


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _parse_bcp_cierre_data(self, available_currencies):
        _logger.info("🚀 Ejecutando _parse_bcp_cierre_data")
        rslt = {}
        available_currency_names = available_currencies.mapped('name')
        fecha_obj = datetime.now() - timedelta(days=1)
        fecha_post = fecha_obj.strftime('%d/%m/%Y')
        fecha_aplicacion = datetime.now().date()

        try:
            url = "https://www.bcp.gov.py/webapps/web/cotizacion/referencial-fluctuante"
            payload = {'fecha': fecha_post}
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Content-Type': 'application/x-www-form-urlencoded',
            }

            response = requests.post(url, data=payload, headers=headers, timeout=15)
            _logger.info("🛰️ Respuesta BCP status: %s", response.status_code)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            table = soup.find('table', class_='table')
            cierre_row = None

            tfoot = table.find('tfoot')
            if tfoot:
                cierre_row = tfoot.find('tr')
                _logger.info("✅ Se encontró el <tfoot> con datos de cierre.")
            else:
                _logger.warning("❌ No se encontró el <tfoot>. Buscando última fila válida del <tbody> como fallback.")
                tbody = table.find('tbody')
                rows = tbody.find_all('tr')
                for row in reversed(rows):
                    cols = row.find_all('td')
                    if len(cols) >= 3 and cols[1].text.strip() and cols[2].text.strip():
                        cierre_row = row
                        _logger.warning("⚠️ Usando última fila del <tbody> como cierre (fallback).")
                        break

            if not cierre_row:
                raise ValueError("No se encontró la fila de cierre.")

            cols = cierre_row.find_all(['th', 'td'])
            compra = Decimal(cols[1].get_text(strip=True).replace('.', '').replace(',', '.'))
            venta = Decimal(cols[2].get_text(strip=True).replace('.', '').replace(',', '.'))

            if compra <= 0 or venta <= 0:
                _logger.warning("❌ Tasa no válida: Compra %s, Venta %s", compra, venta)
                return {}

            base_currency = self.currency_id.name
            _logger.info("💡 Moneda base de la empresa: %s", base_currency)

            if base_currency == 'USD':
                if 'PYG' in available_currency_names:
                    rslt['PYG'] = (compra, fecha_aplicacion)
                rslt['USD'] = (1.0, fecha_aplicacion)

            elif base_currency == 'PYG':
                if 'USD' in available_currency_names:
                    rslt['USD'] = (venta, fecha_aplicacion)
                rslt['PYG'] = (1.0, fecha_aplicacion)

            else:
                _logger.warning("❌ No se soporta la moneda base %s", base_currency)
                return {}

            if base_currency not in rslt:
                rslt[base_currency] = (1.0, fecha_aplicacion)
                _logger.warning("⚠️ Se forzó la inclusión de la moneda base '%s'", base_currency)

            _logger.info("📦 Resultado final devuelto: %s", rslt)
            return rslt

        except Exception as e:
            _logger.exception("💥 Error al obtener tasas BCP: %s", e)
            return {}
