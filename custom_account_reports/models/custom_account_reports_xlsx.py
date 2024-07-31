# pylint: disable=missing-module-docstring,no-name-in-module
import logging
import io
from datetime import datetime
from odoo.tools import base64_to_image
from PIL import Image
from urllib.request import urlopen


import xlsxwriter
from odoo import models

_logger = logging.getLogger(__name__)
class CustomAccountReportsXlsx(models.Model):
    """ Inherit account.reports to make a custom format for the reports
    """

    _inherit = "account.report"

    def _get_report_date(self, options):
        """ Get the date of the report
        """
        print(f"Options: {options}")

        column_groups = options.get('column_groups', {})
        date_from_str = None
        date_to_str = None

        for key, value in column_groups.items():
            forced_options = value.get('forced_options', {})
            date_options = forced_options.get('date', {})
            date_from_str = date_options.get('date_from')
            date_to_str = date_options.get('date_to')
            if date_from_str and date_to_str:
                break
        
        if not date_from_str and not date_to_str:
            return "Date not provided" 
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"Error parsing dates: {date_from_str} or date_to {date_to_str}.Except format 'YYYY-MM-DD'.Original error: {e}")

        return f"Period from {date_from.strftime('%B/%d/%Y')} - {date_to.strftime('%B/%d/%Y')}"

    def _fill_header(self, sheet, row, col_end, stlye):
        for index in range (1, col_end):
            sheet.write(row, index, '', stlye)

    def _add_company_header(self, sheet, options, max_cols, style, small_style):
        """ Add company header to the report
        """

        company_name = self.env.company.name
        report_name = self.name
        formatted_date = self._get_report_date(options)

        sheet.set_default_row(20)
        row = 1

        # Report Name
        sheet.set_row(row, 30)
        sheet.write(row, 0, report_name, style)
        row += 1

        # Company Logo
        # if self.env.company.logo:
        #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        #     url = base_url + '/web/image/res.company/' + str(self.env.company.id) + '/logo'
        #     image_data = io.BytesIO(urlopen(url).read())
        #     sheet.insert_image('B2', url, {'image_data': image_data})

        # Consolidated Companies
        if options.get('consolidation_journals', False):
            consolidated_companies = [journal.get('name').replace('Consolidated Accounting', '') for journal in options.get('consolidation_journals', [])]
            sheet.write(row, 0, ' - '.join(consolidated_companies), small_style)
            row += 1

        # Period
        if options.get("display_dates", False):
            sheet.write(row, 0, "Period: " + options['display_dates'], small_style)
            row += 1

        # Currency
        if options.get("currency", False):
            sheet.write(row, 0, "Currency: " + options['currency'], small_style)
            row += 1

        # Company data
        row += 1
        sheet.write(row, 0, company_name, small_style)
        row += 1
        sheet.write(row, 0, self.env.company.vat, small_style)

    def _inject_report_into_xlsx_sheet(self, options, workbook, sheet):
        def write_with_colspan(sheet, x, y, value, colspan, style):
            if colspan == 1:
                sheet.write(y, x, value, style)
            else:
                sheet.merge_range(y, x, y, x + colspan - 1, value, style)
        
        options['include_currency'] = True
        custom_header_style = workbook.add_format({
            'font_name': 'Calibri', 
            'bold': True, 
            'font_size': 13, 
            'font_color': '#ffffff',
            'align': 'center',
            'bg_color': '#282748'
        })
        
        date_default_col1_style = workbook.add_format({'font_name': 'Inter Medium', 'font_size': 12, 'font_color': '#4F4B81', 'indent': 2, 'num_format': 'yyyy-mm-dd'})
        date_default_style = workbook.add_format({'font_name': 'Inter Medium', 'font_size': 12, 'font_color': '#4F4B81', 'num_format': 'yyyy-mm-dd'})
        default_col1_style = workbook.add_format({'font_name': 'Inter Medium', 'font_size': 12, 'font_color': '#4F4B81', 'indent': 2})
        default_style = workbook.add_format({'font_name': 'Inter Medium', 'font_size': 12, 'font_color': '#4F4B81'})
        title_style = workbook.add_format({'font_name': 'Inter Medium', 'bold': True, 'bottom': 2})
        level_0_style = workbook.add_format({'font_name': 'Inter Medium', 'bold': True, 'font_size': 13, 'bottom': 6, 'font_color': '#4F4B81'})
        level_1_style = workbook.add_format({'font_name': 'Inter Medium', 'bold': True, 'font_size': 13, 'bottom': 1, 'font_color': '#4F4B81'})
        level_2_col1_style = workbook.add_format({'font_name': 'Inter Medium', 'bold': True, 'font_size': 12, 'font_color': '#4F4B81', 'indent': 1})
        level_2_col1_total_style = workbook.add_format({'font_name': 'Inter Medium', 'bold': True, 'font_size': 12, 'font_color': '#4F4B81'})
        level_2_style = workbook.add_format({'font_name': 'Inter Medium', 'bold': True, 'font_size': 12, 'font_color': '#4F4B81'})
        level_3_col1_style = workbook.add_format({'font_name': 'Inter Medium', 'font_size': 12, 'font_color': '#4F4B81', 'indent': 2})
        level_3_col1_total_style = workbook.add_format({'font_name': 'Inter Medium', 'bold': True, 'font_size': 12, 'font_color': '#4F4B81', 'indent': 1})
        level_3_style = workbook.add_format({'font_name': 'Inter Medium', 'font_size': 12, 'font_color': '#4F4B81'})

        level_1_style_float = workbook.add_format({'font_name': 'Inter Medium', 'bold': True, 'font_size': 13, 'bottom': 1, 'font_color': '#000000', 'num_format': '#,##0'})
        level_2_style_float = workbook.add_format({'font_name': 'Inter Medium', 'bold': True, 'font_size': 12, 'font_color': '#000000', 'num_format': '#,##0'})
        level_3_style_float = workbook.add_format({'font_name': 'Inter Medium', 'font_size': 12, 'font_color': '#000000', 'num_format': '#,##0'})

        print_mode_self = self.with_context(no_format=True)
        lines = self._filter_out_folded_children(print_mode_self._get_lines(options))

        # For reports with lines generated for accounts, the account name and codes are shown in a single column.
        # To help user post-process the report if they need, we should in such a case split the account name and code in two columns.
        account_lines_split_names = {}
        for line in lines:
            line_model = self._get_model_info_from_id(line['id'])[0]
            if line_model == 'account.account':
                # Reuse the _split_code_name to split the name and code in two values.
                account_lines_split_names[line['id']] = self.env['account.account']._split_code_name(line['name'])

        # Set the first column width to 70.
        # If we have account lines and split the name and code in two columns, we will also set the second column.
        if len(account_lines_split_names) > 0:
            sheet.set_column(0, 0, 70)
            sheet.set_column(1, 1, 20)
        else:
            sheet.set_column(0, 0, 70)

        original_x_offset = 1 if len(account_lines_split_names) > 0 else 0

        y_offset = 9  # 9 To give space for the header
        # 1 and not 0 to leave space for the line name. original_x_offset allows making place for the code column if needed.
        x_offset = original_x_offset + 1
        
        # Add headers.
        # For this, iterate in the same way as done in main_table_header template
        # column_headers_render_data = self._get_column_headers_render_data(options)
        # for header_level_index, header_level in enumerate(options['column_headers']):
        #     for header_to_render in header_level * column_headers_render_data['level_repetitions'][header_level_index]:
        #         colspan = header_to_render.get('colspan', column_headers_render_data['level_colspan'][header_level_index])
        #         write_with_colspan(sheet, x_offset, y_offset, header_to_render.get('name', ''), colspan, title_style)
        #         x_offset += colspan
        #     if options['show_growth_comparison']:
        #         write_with_colspan(sheet, x_offset, y_offset, '%', 1, title_style)
        #     y_offset += 1
        #     x_offset = original_x_offset + 1

        # for subheader in column_headers_render_data['custom_subheaders']:
        #     colspan = subheader.get('colspan', 1)
        #     write_with_colspan(sheet, x_offset, y_offset, subheader.get('name', ''), colspan, title_style)
        #     x_offset += colspan
        # y_offset += 1
        # x_offset = original_x_offset + 1

        # for column in options['columns']:
        #     colspan = column.get('colspan', 1)
        #     write_with_colspan(sheet, x_offset, y_offset, column.get('name', ''), colspan, title_style)
        #     x_offset += colspan
        # y_offset += 1

        if options.get('order_column'):
            lines = self.sort_lines(lines, options)

        # Add lines.
        for y in range(0, len(lines)):
            level = lines[y].get('level')
            if lines[y].get('caret_options'):
                style = level_3_style
                col1_style = level_3_col1_style
            elif level == 0:
                y_offset += 1
                style = level_0_style
                col1_style = style
            elif level == 1:
                style = level_1_style
                col1_style = style
            elif level == 2:
                style = level_2_style
                col1_style = 'total' in lines[y].get('class', '').split(' ') and level_2_col1_total_style or level_2_col1_style
            elif level == 3:
                style = level_3_style
                col1_style = 'total' in lines[y].get('class', '').split(' ') and level_3_col1_total_style or level_3_col1_style
            else:
                style = default_style
                col1_style = default_col1_style

            # write the first column, with a specific style to manage the indentation
            x_offset = original_x_offset + 1
            if lines[y]['id'] in account_lines_split_names:
                code, name = account_lines_split_names[lines[y]['id']]
                sheet.write(y + y_offset, x_offset - 2, code, col1_style)
                sheet.write(y + y_offset, x_offset - 1, name, col1_style)
            else:
                if lines[y].get('parent_id') and lines[y]['parent_id'] in account_lines_split_names:
                    sheet.write(y + y_offset, x_offset - 2, account_lines_split_names[lines[y]['parent_id']][0], col1_style)
                cell_type, cell_value = self._get_cell_type_value(lines[y])
                if cell_type == 'date':
                    sheet.write_datetime(y + y_offset, x_offset - 1, cell_value, date_default_col1_style)
                else:
                    sheet.write(y + y_offset, x_offset - 1, cell_value, col1_style)

            #write all the remaining cells
            columns = lines[y]['columns']
            if options['show_growth_comparison'] and 'growth_comparison_data' in lines[y]:
                columns += [lines[y].get('growth_comparison_data')]
            for x, column in enumerate(columns, start=x_offset):
                cell_type, cell_value = self._get_cell_type_value(column)
                if cell_type == 'date':
                    sheet.write_datetime(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, date_default_style)
                else:
                    sheet.write(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, style)

        # HEADER
        header_style = workbook.add_format({
            'font_name': 'Inter Medium',
            'bold': False,
            'font_size': 25,
            'align': 'left',
        })
        header_style.set_text_wrap()

        header_small_style = workbook.add_format({
            'font_name': 'Inter Medium',
            'font_size': 14,
            'align': 'left',
        })
        # Add at the end to avoid overwriting the data and know the final y_offset
        self._add_company_header(
            sheet,
            options,
            max_cols=x_offset,
            style=header_style,
            small_style=header_small_style
        )