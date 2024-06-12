# pylint: disable=missing-module-docstring,no-name-in-module

import io
from datetime import datetime

import xlsxwriter
from odoo import models

class CustomAccountReportsXlsx(models.Model):
    """ Inherit account.reports to make a custom format for the reports
    """

    _inherit = "account.report"

    def _get_report_date(self, options):
        """ Get the date of the report
        """

        column_groups = options.get('column_groups', {})
        date_str = None

        for key, value in column_groups.items():
            forced_options = value.get('forced_options', {})
            date_options = forced_options.get('date', {})
            date_str = date_options.get('date_to')
            if date_str:
                break
        
        if not date_str:
            return "Date not provided" 
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"Error parsing date: {date_str}.Except format 'YYYY-MM-DD'.Original error: {e}")

        return date.strftime('As of %B')

    def _fill_header(self, sheet, row, col_end, stlye):
        for index in range (1, col_end):
            sheet.write(row, index, '', stlye)

    def _add_company_header(self, sheet, options, max_cols, style):
        """ Add company header to the report
        """

        company_name = self.env.company.name
        report_name = self.name
        formatted_date = self._get_report_date(options)

        col = 0

        texts = [
            '',
            company_name.upper(),
            report_name.upper(),
            formatted_date.upper(),
            ''
        ]

        for index, text in enumerate(texts):
            sheet.write(index, col, text, style)
            self._fill_header(sheet, index, max_cols, style)


    def export_to_xlsx(self, options, response=None):
        """ Overrides xlsx report to add custom values
        """
        
        def write_with_colspan(sheet, x, y, value, colspan, style):
            if colspan == 1:
                sheet.write(y, x, value, style)
            else:
                sheet.merge_range(y, x, y, x + colspan - 1, value, style)

        self.ensure_one()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {
            'in_memory': True,
            'strings_to_formulas': False,
        })
        sheet = workbook.add_worksheet(self.name[:31])

        custom_header_style = workbook.add_format({
            'font_name': 'Calibri', 
            'bold': True, 
            'font_size': 13, 
            'font_color': '#ffffff',
            'align': 'center',
            'bg_color': '#282748'
        })

        date_default_col1_style = workbook.add_format({'font_name': 'Calibri', 'font_size': 12, 'font_color': '#000000', 'indent': 2, 'num_format': 'yyyy-mm-dd'})
        date_default_style = workbook.add_format({'font_name': 'Calibri', 'font_size': 12, 'font_color': '#000000', 'num_format': 'yyyy-mm-dd'})
        default_col1_style = workbook.add_format({'font_name': 'Calibri', 'font_size': 12, 'font_color': '#000000', 'indent': 2})
        default_style = workbook.add_format({'font_name': 'Calibri', 'font_size': 12, 'font_color': '#000000'})
        title_style = workbook.add_format({'font_name': 'Calibri', 'bold': True, 'bottom': 2})
        level_0_style = workbook.add_format({'font_name': 'Calibri', 'bold': True, 'font_size': 13, 'bottom': 6, 'font_color': '#000000'})
        level_1_style = workbook.add_format({'font_name': 'Calibri', 'bold': True, 'font_size': 13, 'bottom': 1, 'font_color': '#000000'})
        level_2_col1_style = workbook.add_format({'font_name': 'Calibri', 'bold': True, 'font_size': 12, 'font_color': '#000000', 'indent': 1})
        level_2_col1_total_style = workbook.add_format({'font_name': 'Calibri', 'bold': True, 'font_size': 12, 'font_color': '#000000'})
        level_2_style = workbook.add_format({'font_name': 'Calibri', 'bold': True, 'font_size': 12, 'font_color': '#000000'})
        level_3_col1_style = workbook.add_format({'font_name': 'Calibri', 'font_size': 12, 'font_color': '#000000', 'indent': 2})
        level_3_col1_total_style = workbook.add_format({'font_name': 'Calibri', 'bold': True, 'font_size': 12, 'font_color': '#000000', 'indent': 1})
        level_3_style = workbook.add_format({'font_name': 'Calibri', 'font_size': 12, 'font_color': '#000000'})

        level_1_style_float = workbook.add_format({'font_name': 'Calibri', 'bold': True, 'font_size': 13, 'bottom': 1, 'font_color': '#000000', 'num_format': '#,##0'})
        level_2_style_float = workbook.add_format({'font_name': 'Calibri', 'bold': True, 'font_size': 12, 'font_color': '#000000', 'num_format': '#,##0'})
        level_3_style_float = workbook.add_format({'font_name': 'Calibri', 'font_size': 12, 'font_color': '#000000', 'num_format': '#,##0'})

        #Set the first column width to 50
        sheet.set_column(0, 0, 50)

        y_offset = 5
        x_offset = 1 # 5 To live space for the header
        print_mode_self = self.with_context(no_format=True, print_mode=True, prefetch_fields=False)
        #pylint: disable=protected-access
        print_options = print_mode_self._get_options(previous_options=options)
        lines = self._filter_out_folded_children(print_mode_self._get_lines(print_options))

        # Add headers.
        # For this, iterate in the same way as done in main_table_header template
        column_headers_render_data = self._get_column_headers_render_data(print_options)
        for header_level_index, header_level in enumerate(print_options['column_headers']):
            for header_to_render in header_level * column_headers_render_data['level_repetitions'][header_level_index]:
                colspan = header_to_render.get('colspan', column_headers_render_data['level_colspan'][header_level_index])
                write_with_colspan(sheet, x_offset, y_offset, header_to_render.get('name', ''), colspan, title_style)
                x_offset += colspan
            if print_options['show_growth_comparison']:
                write_with_colspan(sheet, x_offset, y_offset, '%', 1, title_style)
            y_offset += 1
            x_offset = 1

        for subheader in column_headers_render_data['custom_subheaders']:
            colspan = subheader.get('colspan', 1)
            write_with_colspan(sheet, x_offset, y_offset, subheader.get('name', ''), colspan, title_style)
            x_offset += colspan
        y_offset += 1
        x_offset = 1

        for column in print_options['columns']:
            colspan = column.get('colspan', 1)
            write_with_colspan(sheet, x_offset, y_offset, column.get('name', ''), colspan, title_style)
            x_offset += colspan
        y_offset += 1

        if print_options.get('order_column'):
            lines = self._sort_lines(lines, print_options)

        # Add lines.
        # pylint: disable=consider-using-enumerate
        style_float = None
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
                style_float = level_1_style_float
                style = level_1_style
                col1_style = style
            elif level == 2:
                style_float = level_2_style_float
                style = level_2_style
                col1_style = 'total' in lines[y].get('class', '').split(' ') and level_2_col1_total_style or level_2_col1_style
            elif level == 3:
                style_float = level_3_style_float
                style = level_3_style
                col1_style = 'total' in lines[y].get('class', '').split(' ') and level_3_col1_total_style or level_3_col1_style
            else:
                style = default_style
                col1_style = default_col1_style

            #write the first column, with a specific style to manage the indentation
            cell_type, cell_value = self._get_cell_type_value(lines[y])
            if cell_type == 'date':
                sheet.write_datetime(y + y_offset, 0, cell_value, date_default_col1_style)
            else:
                sheet.write(y + y_offset, 0, cell_value, col1_style)

            #write all the remaining cells
            columns = lines[y]['columns']
            if print_options['show_growth_comparison'] and 'growth_comparison_data' in lines[y]:
                columns += [lines[y].get('growth_comparison_data')]
            for x, column in enumerate(columns, start=1):
                cell_type, cell_value = self._get_cell_type_value(column)
                if cell_type == 'date':
                    sheet.write_datetime(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, date_default_style)
                else:
                    if isinstance(cell_value, float) and style_float is not None:
                        
                        

                        sheet.write(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, style_float)
                    else:
                        sheet.write(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, style)

        # Add at the finel to avoid overwriting the data and know the final y_offset
        self._add_company_header(
            sheet,
            options,
            max_cols=x_offset,
            style=custom_header_style
        )

        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()

        return {
            'file_name': self.get_default_report_filename('xlsx'),
            'file_content': generated_file,
            'file_type': 'xlsx',
        }
