import base64
import logging
import markupsafe
from odoo import models, fields
from odoo.tools import config, date_utils, get_lang, float_compare, float_is_zero

PISA_COMPANY_ID = 1
PASA_COMPANY_ID = 2
# Only need to change the format of this 2 companies
_logger = logging.getLogger(__name__)


class CustomAccountReportsPdf(models.Model):
    """ Inherit account.reports to make a custom format for the reports
    """

    _inherit = "account.report"

    def _get_currency(self, active_id):
        self.ensure_one()
        consolidation_period = self.env['consolidation.period'].browse(active_id)
        return consolidation_period.chart_currency_id

    def _get_options(self, previous_options=None):
        options = super(CustomAccountReportsPdf, self)._get_options(previous_options)
        if options.get('consolidation_journals', False):
            consolidation_period = self.env['consolidation.period'].browse(options['periods'][0]['id'])
            options.update({
                'currency': consolidation_period.chart_currency_id.name,
                'display_dates': consolidation_period.display_dates
            })
        return options

    def get_company_logo(self):
        """ Get the company logo
        """

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        return base_url + '/web/image/res.company/' + str(self.env.company.id) + '/logo'

    def get_company_primary_color(self):
        """ Get the company primary color
        """

        return self.env.company.primary_color

    def get_company_styles(self):
        """ Get the company styles
        """

        primary_color = self.get_company_primary_color()

        return (
            f"background-color: {primary_color};"
            f"color: {'black' if primary_color == 'gray' else 'white'};"
        )

    def get_formatted_value(self, value):
        """Format the value by removing decimals but keeping the thousand separator."""
        try:
            # Convertimos el valor a float y luego formateamos sin decimales pero con separador de miles
            formatted_value = "{:,.0f}".format(float(value))
        except (ValueError, TypeError):
            # En caso de que la conversión falle, retornamos el valor original
            formatted_value = value
        return formatted_value

    def format_date(self, date_str):
        """ Format the date
        """
        date_obj = fields.Date.from_string(date_str)
        return date_obj.strftime('%d/%m/%Y')

    def get_html(self, options, lines, additional_context=None, template=None):
        template = self.main_template if template is None else template
        report_manager = self._get_report_manager(options)

        render_values = self._get_html_render_values(options, report_manager)
        if additional_context:
            render_values.update(additional_context)

        if options.get('order_column'):
            lines = self._sort_lines(lines, options)

        lines = self._format_lines_for_display(lines, options)
        lines = self._format_lines_for_ellipsis(lines, options)

        # Aplica el formato a todas las columnas
        for line in lines:
            if 'columns' in line:
                for col in line['columns']:
                    if 'no_format' in col:
                        # Aplica el formateo de valores para quitar decimales
                        col['name'] = self.get_formatted_value(col['no_format'])
                    # Asegura que todos los valores tengan la clase 'number'
                    col.update({'class': 'number'})

        # Gestión de números negativos
        for line in lines:
            for col in line['columns']:
                if (
                    isinstance(col.get('no_format'), float)
                    and float_compare(col['no_format'], 0.0, precision_digits=self.env.company.currency_id.decimal_places) == -1
                ):
                    col['class'] += ' color-red'  # Asegúrate de que se agregue correctamente la clase

        render_values['lines'] = lines

        # Maneja las notas al pie si estamos en modo impresión
        if self.env.context.get('print_mode', False):
            footnotes = {str(f.line): f for f in report_manager.footnotes_ids}
            number = 0
            for line in lines:
                f = footnotes.get(str(line.get('id')))
                if f:
                    number += 1
                    line['footnote'] = str(number)
            # Renderizar notas al pie
            footnotes_to_render = [{'id': f.id, 'number': number, 'text': f.text} for f in footnotes.values()]

        # Renderiza el HTML final
        html = self.env['ir.qweb']._render(template, render_values)
        if self.env.context.get('print_mode', False):
            for k, v in self._replace_class().items():
                html = html.replace(k, v)
            # Agrega las notas al pie al HTML
            html = html.replace(markupsafe.Markup('<div class="js_account_report_footnotes"></div>'), self.get_html_footnotes(footnotes_to_render))

        return html