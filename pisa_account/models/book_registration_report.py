from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from unidecode import unidecode
import PyPDF2
import os
import tempfile
import base64
from fpdf import FPDF
from werkzeug.urls import url_encode, url_join
from odoo.tools.misc import format_date, DEFAULT_SERVER_DATE_FORMAT
import logging
import json


def format_number_to_string(number):
    if number == '':
        return ''
    return '{0:,.0f}'.format(int(number)).replace(',', '.')


class CustomPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.start_page_number = 0
        self.signature_image = None
        self.company = None
        self.title = ''
        self.subtitle = False

    def header(self, data=None):
        self.set_font("Arial", "B", 10)
        if self.signature_image:
            self.image(self.signature_image, 165, 10, 45)
        self.cell(0, 2, self.company.name, align="L")
        self.cell(-20, 2, f"Nro: {self.start_page_number + self.page_no()}", align="R", ln=True)
        self.cell(0, 5, self.company.vat, align="L", ln=True)
        self.cell(0, 5, self.company.street if self.company.street else '', align="L", ln=True)
        self.set_font("Arial", "B", 14)
        self.cell(0, 20, self.title, align="C", ln=True)
        if self.subtitle:
            self.cell(0, 10, self.subtitle, align="C", ln=True)


class BookRegistrationReport(models.Model):
    _inherit = 'book.registration.report'

    def daily_book_pdf(self):
        # Override computation to reflect the amounts according to secondary balance
        company = self.env.company
        # Check if the company has a secondary currency set to PYG and is located in PY
        if company.sec_currency_id and company.sec_currency_id.name == "PYG" and company.country_code == "PY":
            TABLE_DATA = [('Cuenta', 'Descripción', 'Detalle', 'Débito', 'Crédito')]
            moves = self.env['account.move'].search(
                [('date', '>=', self.start_date), ('date', '<=', self.end_date), ('state', '=', 'posted')])
            if moves:
                moves = moves.sorted(key=lambda x: (x.date, x.id))
            
            for move in moves:
                TABLE_DATA.append(('Asiento:{0} Fecha: {1}'.format(
                    str(move.id).strip(), str(move.date).strip()), '', '', '', ''))

                for line in move.line_ids:
                    table_line = (
                        unidecode(str(line.account_id.display_name if line.account_id.display_name else ' ').replace(
                            '₲', '').strip()),
                        unidecode(str(line.name if line.name else ' ').replace(
                            '₲', '').strip()),
                        unidecode(str(line.ref if line.ref else ' ').replace(
                            '₲', '').strip()),
                        '{0:,.0f}'.format(abs(int(line.secondary_balance > 0 and line.secondary_balance or 0.0))).replace(
                            ',', '.'),
                        '{0:,.0f}'.format(abs(int(line.secondary_balance < 0 and line.secondary_balance or 0.0))).replace(
                            ',', '.')
                    )
                    TABLE_DATA.append(table_line)

            pdf = CustomPDF()
            pdf.set_font("Arial", "", 6)
            pdf.start_page_number = self.registration_id.current_number
            pdf.company = self.company_id
            pdf.title = "Libro Diario"
            if self.registration_id.signature_image:
                pdf.signature_image = base64.b64decode(
                    self.registration_id.signature_image)
            pdf.add_page()

            with pdf.table(col_widths=(20, 30, 20, 10, 10)) as table:
                for ir, data_row in enumerate(TABLE_DATA):
                    row = table.row()
                    for ic, datum in enumerate(data_row):
                        if ic > 2 and ir > 0:
                            row.cell(text=datum, align='R')
                        else:
                            row.cell(datum)

            pdf_bytes = None
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                pdf.output(tmp_file.name)

                with open(tmp_file.name, "rb") as file:
                    pdf_bytes = file.read()
                    self.page_quantity = PyPDF2.PdfFileReader(file).numPages

            os.remove(tmp_file.name)
            pdf_base64 = base64.b64encode(pdf_bytes)
            self.report_file_name = "Libro_diario.pdf"
            self.write({
                'report_file': pdf_base64
            })
        else:
            super(BookRegistrationReport, self).daily_book_pdf()

    def general_ledger_pdf(self):
        # Override computation to reflect the amounts according to secondary balance
        company = self.env.company
        # Check if the company has a secondary currency set to PYG and is located in PY
        if company.sec_currency_id and company.sec_currency_id.name == "PYG" and company.country_code == "PY":
            invoices = self.env['account.move.line'].search([
                ('parent_state', 'in', ['posted']),
                ('date', '<=', self.end_date),
                ('company_id', '=', self.company_id.id)
            ], order=('id'))
            pdf = CustomPDF()
            pdf.set_font("Arial", "", 6)
            pdf.start_page_number = self.registration_id.current_number
            pdf.company = self.company_id
            pdf.title = "Libro Mayor - Periodo: Del {0} al {1}".format(
                self.start_date, self.end_date)
            if self.registration_id.signature_image:
                pdf.signature_image = base64.b64decode(
                    self.registration_id.signature_image)
            pdf.add_page()
            if not self.detailed:
                query = f"""
                    SELECT
                        ml.account_id,
                        aa.name AS account_name,
                        SUM(CASE
                            WHEN ml.secondary_balance > 0 THEN ml.secondary_balance
                            ELSE 0.0
                        END) AS debit,
                        SUM(CASE
                            WHEN ml.secondary_balance < 0 THEN ml.secondary_balance
                            ELSE 0.0
                        END) AS credit,
                        SUM(ml.secondary_balance) AS balance,
                        aa.code
                    FROM
                        public.account_move_line AS ml
                    INNER JOIN
                        account_account AS aa
                    ON
                        ml.account_id = aa.id
                    WHERE
                        ml.date <= '{self.end_date}'
                        AND ml.company_id = '{self.company_id.id}'
                        AND ml.parent_state = 'posted'
                    GROUP BY
                        ml.account_id,
                        aa.name,
                        aa.code
                    ORDER BY
                        ml.account_id,
                        aa.code
                """

                self.env.cr.execute(query)
                results = self.env.cr.fetchall()

                invoices_grouped = invoices.mapped('account_id')
                TABLE_DATA = [(
                    'Cuenta',
                    'Debe',
                    'Haber',
                    'Saldo'
                )]

                cnt = 0
                total_credit = 0
                total_debit = 0
                total_balance = 0
                for row in results:
                    account_id, account_name, debit, credit, balance, code = row
                    account_name = account_name['en_US']
                    debit = int(debit)
                    credit = abs(int(credit))
                    balance = int(balance)
                    total_debit_t = debit
                    total_credit_t = credit
                    total_balance_t = balance
                    TABLE_DATA.append([
                        # account
                        unidecode(str(code) + ' - ' + \
                                str(account_name).replace('₲', '').strip()),
                        '{0:,.0f}'.format(int(debit)).replace(',', '.'),  # debit
                        '{0:,.0f}'.format(int(credit)).replace(',', '.'),  # credit
                        '{0:,.0f}'.format(int(balance)).replace(
                            ',', '.')  # balance
                    ])
                    total_debit += total_debit_t
                    total_credit += total_credit_t
                    total_balance += total_balance_t

                TABLE_DATA.append([' ',
                                '{0:,.0f}'.format(
                                    int(total_debit)).replace(',', '.'),
                                '{0:,.0f}'.format(
                                    int(total_credit)).replace(',', '.'),
                                '{0:,.0f}'.format(
                                    int(total_balance)).replace(',', '.'),
                                ])

                with pdf.table(col_widths=(60, 15, 15, 15)) as table:
                    for ir, data_row in enumerate(TABLE_DATA):
                        row = table.row()
                        for ic, datum in enumerate(data_row):
                            if ic > 0:  # The second, third, and fourth columns are the last three.
                                row.cell(text=datum, align='R')
                            else:
                                row.cell(datum)
            else:
                TABLE_DATA = [(
                    'Fecha',
                    'Cuenta',
                    'Referencia',
                    'Debe',
                    'Haber',
                    'Saldo'
                )]
                query = f"""
                        WITH subquery AS (
                            SELECT
                                ml.account_id,
                                SUM(CASE WHEN ml.secondary_balance > 0 THEN ml.secondary_balance ELSE 0.0 END) AS debit_total,
                                SUM(CASE WHEN ml.secondary_balance < 0 THEN ml.secondary_balance ELSE 0.0 END) AS credit_total,
                                SUM(ml.secondary_balance) AS balance_total
                            FROM
                                account_move_line AS ml
                            WHERE
                                ml.date < '{self.start_date}' -- Deadline for previous dates
                                AND ml.company_id = '{self.company_id.id}'
                                and ml.parent_state = 'posted'
                            GROUP BY
                                ml.account_id
                        )
                        SELECT
                            ml.date as date,
                            ml.account_id AS account_id,
                            aa.name as account_name,
                            ml.name as account_line_name,
                            CASE WHEN ml.secondary_balance > 0 THEN ml.secondary_balance ELSE 0.0 END as debit,
                            CASE WHEN ml.secondary_balance < 0 THEN ml.secondary_balance ELSE 0.0 END as credit,
                            ml.secondary_balance as balance,
                            sub.debit_total as debit_total,
                            sub.credit_total as credit_total,
                            sub.balance_total as balance_total,
                            aa.id as account_code,
                            am.name as reference,
                            aa.code_store->>'{self.company_id.id}' as code,
                            CASE
                                WHEN aa.name IS NOT NULL THEN 'Dentro del Rango'
                            END as query_state,
                            ml.id as line_code
                        FROM
                            account_move_line AS ml
                        INNER JOIN
                            account_account AS aa ON ml.account_id = aa.id
                        INNER JOIN 
                            account_move as am on ml.move_id = am.id
                        LEFT JOIN
                            subquery as sub ON ml.account_id = sub.account_id
                        WHERE
                            ml.date >= '{self.start_date}'
                            AND ml.date <= '{self.end_date}'
                            AND ml.company_id = '{self.company_id.id}'
                            and ml.parent_state = 'posted'
                        GROUP BY
                            ml.date, ml.account_id, aa.name, ml.name, sub.debit_total, sub.credit_total, sub.balance_total,
                            debit, 
                            credit, 
                            balance, 
                            aa.id, am.name, aa.code_store->>'{self.company_id.id}', ml.id

                    UNION

                        SELECT
                            NULL as date,
                            ml.account_id,
                            aa.name as account_name,
                            Null as account_line_name,
                            0 as debit,
                            0 as credit,
                            0 as balance,
                            SUM(CASE WHEN ml.secondary_balance > 0 THEN ml.secondary_balance ELSE 0.0 END) AS debit_total,
                            SUM(CASE WHEN ml.secondary_balance < 0 THEN ml.secondary_balance ELSE 0.0 END) AS credit_total,
                            SUM(ml.secondary_balance) AS balance_total,
                            aa.id as account_code,
                            NULL as reference,
                            aa.code_store->>'{self.company_id.id}' as code,
                            CASE
                                WHEN aa.name IS NOT NULL THEN 'Otras Cuentas'
                            END as query_state,
                            NULL as line_code
                        FROM
                            public.account_move_line AS ml
                        INNER JOIN
                            account_account AS aa ON ml.account_id = aa.id
                        WHERE
                            ml.date < '{self.start_date}'
                            AND ml.company_id = '{self.company_id.id}'
                            AND ml.parent_state = 'posted'
                            AND NOT EXISTS (
                                SELECT 1
                                FROM public.account_move_line AS ml_sub
                                WHERE
                                        ml_sub.account_id = ml.account_id
                                        AND ml_sub.date >= '{self.start_date}'
                                        AND ml_sub.date <= '{self.end_date}'
                                        AND ml_sub.company_id = '{self.company_id.id}'
                                        AND ml_sub.parent_state = 'posted'
                            )
                        GROUP BY
                            ml.account_id, aa.name, aa.code_store->>'{self.company_id.id}', aa.id

                    ORDER BY
                        ---ml.account_id, ml.date,aa.code
                        code, reference
                        ---, date DESC;

                """

                self.env.cr.execute(query)
                results = self.env.cr.fetchall()
                account_name_group = []

                for row in results:
                    date, account_id, account_name, account_line_name, debit, credit, balance, debit_total, credit_total, balance_total, account_code, reference, code, query_state, line_code = row
                    if account_id not in [item['account'] for item in account_name_group]:
                        account_name = account_name['en_US']
                        a = {
                            'account': account_id,
                            'account_name': account_name,
                            'debit_total': abs(debit),
                            'credit_total': abs(credit),
                            'balance_total': abs(balance),
                            'code': code,
                            'query_state': query_state

                        }
                        account_name_group.append(a)

                total_credit_final = 0
                total_debit_final = 0
                total_balance_final = 0

                total_debit_no_details = 0
                total_credit_no_details = 0
                total_balance_no_details = 0

                for item in account_name_group:
                    total_credit = 0
                    total_debit = 0
                    total_balance = 0
                    if not item['debit_total']:
                        debit_total = 0
                    else:
                        debit_total = item['debit_total']

                    debit_total_balance = debit_total

                    if not item['credit_total']:
                        credit_total = 0
                    else:
                        credit_total = item['credit_total']

                    credit_total_balance = credit_total

                    if not item['balance_total']:
                        balance_total = 0
                    else:
                        balance_total = item['balance_total']

                    balance_total_balance = balance_total

                    TABLE_DATA.append([
                        '',
                        # account
                        unidecode(
                            str(item['code']) + ' - ' + str(item['account_name']).replace('₲', '').strip()),
                        '',
                        '',
                        '',
                        '',
                    ])
                    TABLE_DATA.append([
                        '',
                        'Saldo inicial',
                        '',
                        '{0:,.0f}'.format(int(debit_total)).replace(',', '.'),
                        '{0:,.0f}'.format(int(credit_total)).replace(',', '.'),
                        '{0:,.0f}'.format(int(balance_total)).replace(',', '.'),
                    ])
                    reference_balance_computation = 0
                    cnt = 0
                    for row in results:
                        date, account_id, account_name, account_line_name, debit, credit, balance, debit_total, credit_total, balance_total, account_code, referencia, code, query_state, line_code = row
                        if item['query_state'] == 'Dentro del Rango':
                            if account_id == item['account']:
                                if not account_line_name:
                                    account_line_name = ''
                                else:
                                    account_line_name = str(
                                        account_line_name).replace('₲', '').strip()
                                total_debit_t = debit
                                total_credit_t = credit
                                total_balance_t = balance
                                if not date:
                                    date = ''
                                else:
                                    date = str(date.strftime("%d/%m/%y"))
                                if reference:
                                    reference = reference
                                else:
                                    reference = ''
                                cnt += 1

                                if cnt == 1:
                                    reference_balance_computation = (
                                        balance_total_balance + debit) - credit
                                else:
                                    c = reference_balance_computation
                                    reference_balance_computation = (c + debit) - credit

                                TABLE_DATA.append([
                                    date,
                                    '',
                                    unidecode(reference),
                                    '{0:,.0f}'.format(
                                        int(debit)).replace(',', '.'),
                                    '{0:,.0f}'.format(
                                        int(credit)).replace(',', '.'),
                                    '{0:,.0f}'.format(
                                        int(reference_balance_computation)).replace(',', '.'),
                                ])
                                total_debit += total_debit_t
                                total_credit += total_credit_t
                                total_balance += total_balance_t

                                total_debit_final += total_debit_t
                                total_credit_final += total_credit_t
                                total_balance_final += total_balance_t

                    if item['query_state'] == 'Dentro del Rango':

                        # We add the total of the initial balance and the total of the account lines by accounts
                        # Debit
                        if debit_total_balance > 0 and total_debit > 0:
                            total_debit_total_initial_balance = debit_total_balance + total_debit

                        elif debit_total_balance > 0 and total_debit == 0:
                            total_debit_total_initial_balance = debit_total_balance

                        else:
                            total_debit_total_initial_balance = total_debit
                        # Credit
                        if credit_total_balance > 0 and total_credit > 0:
                            total_credit_total_initial_balance = credit_total_balance + total_credit

                        elif credit_total_balance > 0 and total_credit == 0:
                            total_credit_total_initial_balance = credit_total_balance

                        else:
                            total_credit_total_initial_balance = total_credit

                        # Balance
                        if balance_total_balance != 0 and total_balance != 0:
                            total_balance_total_initial_balance = balance_total_balance + total_balance
                        else:
                            total_balance_total_initial_balance = total_balance

                        TABLE_DATA.append([
                            ' ',
                            'Total ' + unidecode(str(item['code'])) + ' - ' + unidecode(
                                # account
                                str(item['account_name']).replace('₲', '').strip()),
                            ' ',
                            '{0:,.0f}'.format(
                                int(total_debit_total_initial_balance)).replace(',', '.'),
                            '{0:,.0f}'.format(
                                int(total_credit_total_initial_balance)).replace(',', '.'),
                            '{0:,.0f}'.format(
                                int(total_balance_total_initial_balance)).replace(',', '.'),
                        ])
                    else:
                        TABLE_DATA.append([
                            ' ',
                            'Total ' + unidecode(str(item['code'])) + ' - ' + unidecode(
                                # account
                                str(item['account_name']).replace('₲', '').strip()),
                            ' ',
                            '{0:,.0f}'.format(
                                int(debit_total_balance)).replace(',', '.'),
                            '{0:,.0f}'.format(
                                int(credit_total_balance)).replace(',', '.'),
                            '{0:,.0f}'.format(
                                int(balance_total_balance)).replace(',', '.'),

                        ])

                if debit_total_balance > 0:
                    result_debit = total_debit_no_details + total_debit_final
                else:
                    result_debit = total_debit_final

                if credit_total_balance > 0:
                    total_credit_no_details += credit_total_balance
                    result_credit = total_credit_no_details + total_credit_final
                else:
                    result_credit = total_credit_final

                if balance_total_balance != 0:
                    total_balance_no_details += balance_total_balance
                    result_balance = total_balance_no_details + total_balance_final
                else:
                    result_balance = total_balance_final

                TABLE_DATA.append([
                    ' ',
                    ' ',
                    ' ',
                    '{0:,.0f}'.format(int(result_debit)).replace(',', '.'),
                    '{0:,.0f}'.format(int(result_credit)).replace(',', '.'),
                    '{0:,.0f}'.format(int(result_balance)).replace(',', '.'),
                ])

                TABLE_DATA = self.format_table_data(TABLE_DATA)

                with pdf.table(col_widths=(10, 50, 50, 15, 15, 15)) as table:
                    for ir, data_row in enumerate(TABLE_DATA):
                        row = table.row()
                        for ic, datum in enumerate(data_row):
                            if ic >= 3:  # Align the last three columns to the right.
                                row.cell(text=datum, align='R')
                            else:
                                row.cell(datum)

            pdf_bytes = None
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                pdf.output(tmp_file.name)

                with open(tmp_file.name, "rb") as file:
                    pdf_bytes = file.read()
                    self.page_quantity = PyPDF2.PdfFileReader(file).numPages

            os.remove(tmp_file.name)
            pdf_base64 = base64.b64encode(pdf_bytes)
            self.report_file_name = "Libro_mayor.pdf"
            self.write({
                'report_file': pdf_base64
            })
        else:
            return super(BookRegistrationReport, self).general_ledger_pdf()

    def inventory_pdf(self):
        # Override computation to reflect the amounts according to secondary balance
        company = self.env.company
        # Check if the company has a secondary currency set to PYG and is located in PY
        if company.sec_currency_id and company.sec_currency_id.name == "PYG" and company.country_code == "PY":

            TABLE_DATA_BS = [
                [
                    'Cantidad',
                    'Detalle',
                    'Precio Unitario',
                    'Subtotal',
                    'Total',
                ],
            ]

            TABLE_DATA_IS = TABLE_DATA_BS.copy()
            debug_mode = False

            previous_options = {
                'single_company': [1],
                'fiscal_position': 'all',
                'date': {
                    'string': str(self.end_date.year),
                    'period_type': 'fiscalyear',
                    'mode': 'range',
                    'date_from': str(self.end_date.year) + '-01-01',
                    'date_to': str(self.end_date.year) + '-12-31',
                    'filter': 'custom'},
                'comparison': {'filter': 'no_comparison',
                            'number_period': 1,
                            'date_from': str(self.end_date.year) + '-01-01',
                            'date_to': str(self.end_date.year) + '-12-31',
                            'periods': []},
                'all_entries': False,
                'analytic': True,
                'unreconciled': True,
                'unfold_all': True,
                'analytic_groupby': True,
                'analytic_plan_groupby': True,
                'include_analytic_without_aml': False,
                'unposted_in_period': False,
                'export_mode': False,
                'column_headers': {},
                'column_groups': {},
                'columns': {},
                'companies': [],
                'show_debug_column': False,
                'unfolded_lines': [],
            }

            def print_account(env, expression_id, account_id, padding=0, hide_empty_lines=True,):
                global expressions_totals
                table_lines = []
                table_line = []
                account_id_dict = expressions_totals[expression_id][account_id]
                if hide_empty_lines and \
                        not any(account_id_dict.get(balance_type) for balance_type in ['account_balance', 'pending_outbound', 'pending_inbound']) and \
                        not debug_mode:
                    return
                show_account_detail_mode = account_id_dict.get(
                    'show_account_detail_mode')
                table_line += [''] * padding
                table_line.append(account_id.code + '-' + account_id.name)
                if debug_mode:
                    table_line.append(account_id.id)
                    table_line.append(show_account_detail_mode)
                table_line += [''] * 2
                table_line.append(account_id_dict.get('account_total'))
                table_lines.append(table_line)
                if show_account_detail_mode == 'mode_account_balance':
                    table_line = []
                    table_line += [''] * padding
                    table_line.append('Saldo Conciliado')
                    table_line += ['']
                    table_line.append(account_id_dict.get('account_balance'))
                    table_line += ['']
                    table_lines.append(table_line)
                    table_line = []

                    table_line += [''] * padding
                    table_line.append('Pagos pendientes de conciliación')
                    table_line += ['']
                    table_line.append(account_id_dict.get('pending_outbound'))
                    table_line += ['']
                    table_lines.append(table_line)
                    table_line = []

                    table_line += [''] * padding
                    table_line.append('Recibos pendientes de conciliación')
                    table_line += ['']
                    table_line.append(account_id_dict.get('pending_inbound'))
                    table_line += ['']
                    table_lines.append(table_line)
                    table_line = []

                elif show_account_detail_mode == 'mode_account_partners':
                    account_move_line_ids = account_id_dict.get(
                        'account_move_line_ids')
                    if account_move_line_ids:
                        partner_ids = account_move_line_ids.mapped('partner_id')
                        partner_ids_list = list(partner_ids)
                        if account_id_dict.get('account_move_line_ids').filtered(lambda x: not x.partner_id):
                            partner_ids_list.append(partner_ids.browse())
                        for partner_id in partner_ids_list:
                            table_line = []
                            account_move_line_ids_partner = account_id_dict.get('account_move_line_ids').filtered(
                                lambda x: x.partner_id == partner_id
                            )
                            table_line += [''] * padding
                            table_line.append(
                                partner_id.name if partner_id else 'Sin nombre')
                            table_line.append(sum(
                                account_move_line.amount_residual for account_move_line in account_move_line_ids_partner))
                            table_line += [''] * 2
                            table_lines.append(table_line)
                elif show_account_detail_mode == 'mode_account_inventory':
                    if env.ref('base.module_stock').state in ['installed', 'to upgrade']:
                        stock_valuation_layer_ids = env['stock.valuation.layer'].search([
                            ('product_id.categ_id.property_stock_valuation_account_id',
                            '=', account_id.id),
                        ])
                        for product_id in stock_valuation_layer_ids.product_id:
                            table_line = []
                            stock_valuation_layers_product_id = stock_valuation_layer_ids.filtered(
                                lambda x: x.product_id == product_id)

                            stock_valuation_layers_product_id_quantity = sum(
                                stock_valuation_layer_product_id.quantity for stock_valuation_layer_product_id in stock_valuation_layers_product_id
                            )

                            stock_valuation_layers_product_id_value = sum(
                                stock_valuation_layer_product_id.value for stock_valuation_layer_product_id in stock_valuation_layers_product_id
                            )

                            stock_valuation_layers_product_id_unit_cost = 0
                            if stock_valuation_layers_product_id_value and stock_valuation_layers_product_id_quantity:
                                stock_valuation_layers_product_id_unit_cost = stock_valuation_layers_product_id_value / \
                                    stock_valuation_layers_product_id_quantity

                            table_line += [''] * (padding - 1)
                            table_line.append(
                                stock_valuation_layers_product_id_quantity)
                            table_line.append(product_id.name)
                            table_line.append(
                                stock_valuation_layers_product_id_unit_cost)
                            table_line.append(
                                stock_valuation_layers_product_id_value)
                            table_lines.append(table_line)
                elif show_account_detail_mode == 'mode_account_asset_fixed':
                    account_assets = env['account.asset'].search([
                        ('state', 'in', ['open', 'close']),
                        ('account_asset_id', '=', account_id.id),
                    ])
                    for account_asset in account_assets:
                        table_line = []
                        table_line += [''] * padding
                        table_line.append(account_asset.name)
                        if account_asset.state == 'open' and not account_id.asset_model:
                            table_line.append(account_asset.original_value)
                        elif account_asset.state == 'close' or \
                                account_asset.state == 'open' and account_id.asset_model:
                            table_line.append(account_asset.book_value)
                        table_line += [''] * 2
                        table_lines.append(table_line)
                for table_line in table_lines:
                    TABLE_DATA.append(table_line)

            def print_accounts_by_group(env, expression_id, padding, hide_empty_lines, group_ids, allowed_account_group_ids, account_ids,):
                for group_id in group_ids:
                    child_group_ids = group_ids.search(
                        [('parent_id', '=', group_id.id), ('id', 'in', allowed_account_group_ids.ids)])
                    for account_group_id in child_group_ids:
                        table_line = []
                        account_group_for_total_ids = account_group_id
                        while True:
                            account_group_child_ids = account_group_for_total_ids.search([
                                ('parent_id', 'in', account_group_for_total_ids.ids),
                                ('id', 'not in', account_group_for_total_ids.ids),
                            ])
                            if account_group_child_ids:
                                account_group_for_total_ids |= account_group_child_ids
                            else:
                                break

                        account_group_total = sum([
                            expressions_totals[expression_id][account_id].get('account_total') for account_id in account_ids.search([
                                ('id', 'in', account_ids.ids),
                                ('group_id', 'in', account_group_for_total_ids.ids),
                            ])
                        ])

                        table_line += [''] * padding
                        table_line.append(account_group_id.name)
                        table_line += [''] * 2
                        table_line.append(account_group_total)
                        TABLE_DATA.append(table_line)

                        for account_id in account_ids.filtered(lambda account: account.group_id == account_group_id):
                            print_account(
                                env=env,
                                expression_id=expression_id,
                                account_id=account_id,
                                padding=padding,
                                hide_empty_lines=hide_empty_lines,
                            )
                        print_accounts_by_group(
                            env=env,
                            expression_id=expression_id,
                            padding=padding,
                            hide_empty_lines=hide_empty_lines,
                            group_ids=account_group_id,
                            allowed_account_group_ids=allowed_account_group_ids,
                            account_ids=account_ids,
                        )

            def print_report_lines(
                    env,
                    report_lines,
                    padding,
                    headers,
                    quantity_headers,
                    hide_empty_lines,
                    force_print_from_report_totals,
                    force_report_totals,
                    account_report_id,
            ):
                table_line = []

                global expressions_totals

                if headers:
                    headers = False

                for report_line in report_lines:
                    if force_print_from_report_totals and \
                            force_report_totals or \
                            (
                                force_report_totals and
                                ('cross_report' in [expression_id.subformula for expression_id in report_line.expression_ids]) or
                                (not report_line.foldable and not report_line.hide_if_zero)
                            ):
                        report_line_total = sum(
                            force_report_totals.get(expression_id.id).get('value') for expression_id in report_line.expression_ids
                        )
                    else:
                        report_line_total = sum(
                            sum(
                                expressions_totals[expression_id][account_id].get(
                                    'account_total')
                                for account_id in expressions_totals[expression_id]
                            )
                            for expression_id in
                            report_line.search([('id', 'child_of', report_line.ids)]).expression_ids.filtered(
                                lambda x: x.engine == 'domain')
                        )

                for report_line in report_lines:
                    report_line_total = sum(
                        sum(
                            expressions_totals[expression_id][account_id].get(
                                'account_total')
                            for account_id in expressions_totals[expression_id]
                        )
                        for expression_id in
                        report_line.search([('id', 'child_of', report_line.ids)]).expression_ids.filtered(
                            lambda x: x.engine == 'domain')
                    )

                    if hide_empty_lines and not report_line_total and not debug_mode:
                        continue
                    table_line = []
                    table_line += [''] * padding
                    table_line.append(report_line.name)
                    if debug_mode:
                        # ONLY PRESENT IN DEBUG MODE
                        table_line.append(report_line.id)
                    table_line += [''] * 2
                    table_line.append(report_line_total)

                    report_line_expressions = report_line.expression_ids.filtered(
                        lambda x: x.engine == 'domain')
                    for expression_id in report_line_expressions:
                        if account_report_id.filter_hierarchy == 'by_default':
                            account_ids = env['account.account'].browse(
                                [a.id for a in expressions_totals[expression_id]])
                            account_group_ids = account_ids.group_id
                            while True:
                                account_group_parent_ids = account_group_ids.parent_id.filtered(
                                    lambda x: x not in account_group_ids)
                                if account_group_parent_ids:
                                    account_group_ids |= account_group_parent_ids
                                else:
                                    break
                            root_group_ids = account_group_ids.filtered(
                                lambda x: not x.parent_id)

                            print_accounts_by_group(
                                env=env,
                                expression_id=expression_id,
                                padding=padding,
                                hide_empty_lines=hide_empty_lines,
                                group_ids=root_group_ids,
                                allowed_account_group_ids=account_group_ids,
                                account_ids=account_ids,
                            )
                        else:
                            for account_id in expressions_totals[expression_id]:
                                print_account(
                                    env,
                                    expression_id,
                                    account_id,
                                    padding=padding,
                                    hide_empty_lines=hide_empty_lines,
                                )
                    TABLE_DATA.append(table_line)
                    print_report_lines(
                        env=env,
                        report_lines=report_line.children_ids,
                        padding=padding,
                        headers=headers,
                        quantity_headers=quantity_headers,
                        hide_empty_lines=hide_empty_lines,
                        force_print_from_report_totals=force_print_from_report_totals,
                        force_report_totals=force_report_totals,
                        account_report_id=account_report_id,
                    )

            # BALANCE SHEET

            TABLE_DATA = TABLE_DATA_BS
            bs = self.company_id.inventory_book_base_report_bs
            if not bs:
                raise ValidationError(_
                                    ('A base report for the Balance Sheet of the Inventory Book report is not set. '
                                    'Please go to the accounting settings to establish the necessary parameters.'))
            previous_options.update({'report_id': bs.id})
            bs_options = bs.get_options(previous_options)
            bs_info = bs.get_report_information(bs_options)
            bs_info = bs_info.get('column_groups_totals')
            bs_info = bs_info.get(list(bs_info.keys())[0])
            # The content of this variable will be calculated outside the function that prints the lines; 
            # therefore, it is declared as a global variable.
            global expressions_totals
            # All the account values to be printed will go here.
            expressions_totals = {}
            expression_ids = bs.line_ids.expression_ids.filtered(
                lambda x: x.engine == 'domain')
            # The expressions of the lines that form the report structure are filtered; 
            # only the expressions that use 'domain' for calculating their content will be used.

            for expression_id in expression_ids:
                expressions_totals[expression_id] = {}
                aml_ids = eval("self.env['account.move.line'].search(" + expression_id.formula + ")")
                # Each expression to be processed has a domain to obtain the accounting entries, from which the accounts to be processed must be obtained.
                for account_id in aml_ids.mapped('account_id').filtered(
                    lambda x:
                    x.account_type in [
                        'asset_cash',
                        'asset_receivable',
                        'asset_current',
                        'asset_non_current',
                        'asset_fixed',
                        'liability_payable',
                        'liability_current',
                        'liability_non_current',
                        'equity',
                    ]
                    and x not in (
                        x.company_id.account_journal_payment_debit_account_id,
                        x.company_id.account_journal_payment_credit_account_id,
                    )).sorted(key=lambda x: x.code):

                    # BALANCE AS OF DATE
                    account_move_line_ids = aml_ids.search(domain=[
                        ('account_id', '=', account_id.id),
                        ('parent_state', '=', 'posted'),
                        ('date', '<=', previous_options['date']['date_to'])
                    ])
                    if account_move_line_ids:
                        account_balance = sum(
                            account_move_line_ids.mapped('balance'))
                    else:
                        account_balance = 0
                    account_outbound = 0
                    account_inbound = 0
                    for move_type in ['outbound', 'inbound']:
                        self.env.cr.execute("""
                                    SELECT SUM(amount_company_currency_signed) AS amount_total_company
                                    FROM account_payment payment
                                    JOIN account_move move ON move.payment_id = payment.id
                                    WHERE payment.is_matched IS NOT TRUE
                                    AND payment.payment_type = %s
                                    AND move.state = 'posted'
                                    AND move.journal_id = ANY(%s)
                                    GROUP BY move.company_id, move.journal_id, move.currency_id
                                        """, [move_type, self.env['account.journal'].search(
                            [('default_account_id', '=', account_id.id)]).ids])  # Debemos obtener todos los saldos pendientes de conciliar para la cuenta
                        query_result = self.env.cr.fetchall()
                        amount_result = sum(sum(j for j in t)
                                            for t in query_result)
                        if move_type == 'outbound':
                            account_outbound = -amount_result
                        if move_type == 'inbound':
                            account_inbound = amount_result

                        # Determine the detail mode for the account.
                        # In 'mode_account_balance' mode, the reconciled balance and outstanding reconciliation of incoming and outgoing are detailed.
                        # In 'mode_account_partners' mode, the outstanding reconciliation balances are detailed but grouped by supplier or customer.
                        # In 'mode_account_inventory' mode, the inventory valuation is detailed.
                        # In 'mode_account_asset_fixed' mode, the valuation of fixed assets is detailed.

                        show_account_detail_mode = False

                        if account_id.account_type == 'asset_cash' and not account_id.reconcile:
                            show_account_detail_mode = 'mode_account_balance'

                        elif (account_id.account_type == 'asset_receivable' and account_id.reconcile) or \
                                (account_id.account_type == 'liability_payable' and account_id.reconcile):
                            show_account_detail_mode = 'mode_account_partners'

                        elif account_id.account_type == 'asset_current' and not account_id.reconcile and account_id.create_asset in ['no']:
                            show_account_detail_mode = 'mode_account_inventory'

                        elif (account_id.account_type == 'asset_fixed') or \
                                (account_id.account_type == 'liability_current') or \
                                (
                            account_id.account_type == 'asset_current' and
                            not account_id.reconcile and
                            account_id.create_asset in ['draft', 'validate'] and
                            account_id.asset_model
                        ):
                            show_account_detail_mode = 'mode_account_asset_fixed'

                        if expression_id.subformula == '-sum':
                            account_balance *= -1
                            account_inbound *= -1
                            account_outbound *= -1

                        expressions_totals[expression_id][account_id] = {
                            'account_total': account_balance + account_inbound - account_outbound,
                            'account_move_line_ids': account_move_line_ids,
                            'account_balance': account_balance,
                            'pending_outbound': account_outbound,
                            'pending_inbound': account_inbound,
                            'show_account_detail_mode': show_account_detail_mode,
                        }

            print_report_lines(
                env=self.env,
                report_lines=bs.line_ids.filtered(
                    lambda x: not x.parent_id),
                padding=1,
                headers=True,
                quantity_headers=True,
                hide_empty_lines=True,
                force_print_from_report_totals=False,
                force_report_totals=bs_info,
                account_report_id=bs,
            )

            # INCOME STATEMENT

            TABLE_DATA = TABLE_DATA_IS
            isrep = self.company_id.inventory_book_base_report_is
            if not isrep:
                raise ValidationError(_(
                    'A base report for the Income Statement of the Inventory Book report '
                    'is not set. Please go to the accounting settings to establish the '
                    'necessary parameters.'
                ))
            
            previous_options.update({'report_id': isrep.id})
            isrep_options = isrep.get_options(previous_options)
            isrep_info = isrep.get_report_information(isrep_options)
            isrep_info = isrep_info.get('column_groups_totals')
            isrep_info = isrep_info.get(list(bs_info.keys())[0])

            # All the account values to be printed will go here.
            expressions_totals = {}

            expression_ids = []
            expression_ids = isrep.line_ids.expression_ids.filtered(
                lambda x: x.engine == 'domain')
            # The expressions of the lines that form the report structure are filtered;
            # only the expressions that use 'domain' for calculating their content will be used.
            for expression_id in expression_ids:
                expressions_totals[expression_id] = {}
                aml_ids = eval(
                    "self.env['account.move.line'].search(" + expression_id.formula + ")")
                # Each expression to be processed has a domain to obtain the accounting entries, 
                # from which the accounts to be processed must be obtained.
                for account_id in aml_ids.mapped('account_id').filtered(
                        lambda x:
                        x.account_type in [
                            'income',
                            'expense',
                            'expense_depreciation',
                            'income_other',
                        ]
                        and x not in (
                            x.company_id.account_journal_payment_debit_account_id,
                            x.company_id.account_journal_payment_credit_account_id,
                        )
                ).sorted(key=lambda x: x.code):

                    # BALANCE AS OF DATE
                    account_move_line_ids = aml_ids.search(domain=[
                        ('account_id', '=', account_id.id),
                        ('parent_state', '=', 'posted'),
                        ('date', '<=', previous_options['date']['date_to'])
                    ])
                    if account_move_line_ids:
                        account_balance = sum(
                            account_move_line_ids.mapped('balance'))
                    else:
                        account_balance = 0
                    account_outbound = 0
                    account_inbound = 0
                    for move_type in ['outbound', 'inbound']:
                        self.env.cr.execute("""
                                    SELECT SUM(amount_company_currency_signed) AS amount_total_company
                                    FROM account_payment payment
                                    JOIN account_move move ON move.original_payment_id = payment.id
                                    WHERE payment.is_matched IS NOT TRUE
                                    AND payment.payment_type = %s
                                    AND move.state = 'posted'
                                    AND move.journal_id = ANY(%s)
                                GROUP BY move.company_id, move.journal_id, move.currency_id
                                """, [move_type, self.env['account.journal'].search(
                            [('default_account_id', '=', account_id.id)]).ids])  # Debemos obtener todos los saldos pendientes de conciliar para la cuenta
                        query_result = self.env.cr.fetchall()
                        amount_result = sum(sum(j for j in t)
                                            for t in query_result)
                        if move_type == 'outbound':
                            account_outbound = -amount_result
                        if move_type == 'inbound':
                            account_inbound = amount_result

                        # Determine the detail mode for the account.
                        # In 'mode_account_balance' mode, the reconciled balance and the outstanding reconciliation of incoming and outgoing are detailed.
                        # In 'mode_account_partners' mode, the outstanding reconciliation balances are detailed but grouped by supplier or customer.
                        # In 'mode_account_inventory' mode, the inventory valuation is detailed.
                        # In 'mode_account_asset_fixed' mode, the valuation of fixed assets is detailed.
                        show_account_detail_mode = False

                        if expression_id.subformula == '-sum':
                            account_balance *= -1
                            account_inbound *= -1
                            account_outbound *= -1

                        expressions_totals[expression_id][account_id] = {
                            'account_total': account_balance + account_inbound - account_outbound,
                            'account_move_line_ids': account_move_line_ids,
                            'account_balance': account_balance,
                            'pending_outbound': account_outbound,
                            'pending_inbound': account_inbound,
                            'show_account_detail_mode': show_account_detail_mode,
                        }

            print_report_lines(
                env=self.env,
                report_lines=isrep.line_ids.filtered(
                    lambda x: not x.parent_id),
                padding=1,
                headers=True,
                quantity_headers=False,
                hide_empty_lines=True,
                force_print_from_report_totals=True,
                force_report_totals=isrep_info,
                account_report_id=isrep,
            )

            pdf = CustomPDF()
            pdf.set_font("Arial", "", 6)
            pdf.start_page_number = self.registration_id.current_number
            pdf.company = self.company_id
            if self.registration_id.signature_image:
                pdf.signature_image = base64.b64decode(
                    self.registration_id.signature_image)

            for TABLE_DATA in [TABLE_DATA_BS, TABLE_DATA_IS]:
                if TABLE_DATA == TABLE_DATA_BS:
                    pdf.title = "Libro Inventario - Balance General"
                if TABLE_DATA == TABLE_DATA_IS:
                    pdf.title = "Libro Inventario - Estado de Resultados"
                pdf.add_page()

                TABLE_DATA = self.format_table_data(TABLE_DATA)
                
                with pdf.table(col_widths=(20, 30, 20, 10, 10)) as table:
                    for line_count, data_row in enumerate(TABLE_DATA):
                        row = table.row()
                        for column_count, data in enumerate(data_row):
                            if column_count > 1 and line_count > 0:
                                row.cell(text=format_number_to_string(
                                    data), align='R')
                            else:
                                row.cell(text=str(data), align='L')

            pdf_bytes = None
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                pdf.output(tmp_file.name)

                with open(tmp_file.name, "rb") as file:
                    pdf_bytes = file.read()
                    self.page_quantity = PyPDF2.PdfFileReader(file).numPages

            os.remove(tmp_file.name)
            pdf_base64 = base64.b64encode(pdf_bytes)
            self.report_file_name = "Libro_inventario.pdf"
            self.write({
                'report_file': pdf_base64
            })
        else:
            return super(BookRegistrationReport, self).inventory_pdf()
    
    def daily_month_summary_pdf(self):
        # Override computation to reflect the amounts according to secondary balance
        company = self.env.company
        # Check if the company has a secondary currency set to PYG and is located in PY
        if company.sec_currency_id and company.sec_currency_id.name == "PYG" and company.country_code == "PY":
            
            TABLE_DATA = [('Cuenta', 'Débito', 'Crédito')]
            moves = self.env['account.move'].search(
                [('date', '>=', self.start_date), ('date', '<=', self.end_date), ('state', '=', 'posted')])

            if moves:
                years = set(moves.sorted(key=lambda x: x.date).mapped(
                    lambda x: x.date.year))
                months = set(moves.sorted(key=lambda x: x.date).mapped(
                    lambda x: x.date.month))
                moves = moves.sorted(key=lambda x: (x.date, x.id))
                total_gral_debit = 0
                total_gral_credit = 0
                for year in years:
                    for month in months:
                        total_debit = 0
                        total_credit = 0
                        TABLE_DATA.append(('Fecha: %s/%s' % (month, year), '', ''))
                        month_moves = moves.filtered(
                            lambda x: x.date.month == month and x.date.year == year)
                        month_move_lines_debits = month_moves.mapped(
                            'line_ids').filtered(lambda x: x.debit > 0)
                        month_move_lines_debits_accts = sorted(list(
                            set(month_move_lines_debits.mapped('account_id'))), key=lambda x: x.display_name)
                        for account in month_move_lines_debits_accts:
                            debit = sum(month_move_lines_debits.filtered(
                                lambda x: x.account_id == account and x.debit > 0).mapped('secondary_balance'))
                            credit = abs(sum(month_move_lines_debits.filtered(
                                lambda x: x.account_id == account and x.credit < 0).mapped('secondary_balance')))
                            table_line = (
                                account.display_name,
                                '{0:,.0f}'.format(debit),
                                '{0:,.0f}'.format(credit),
                            )
                            total_debit += debit
                            total_credit += credit
                            total_gral_debit += debit
                            total_gral_credit += credit
                            TABLE_DATA.append(table_line)
                        month_move_lines_credits = month_moves.mapped(
                            'line_ids').filtered(lambda x: x.credit > 0)
                        month_move_lines_credits_accts = sorted(list(
                            set(month_move_lines_credits.mapped('account_id'))), key=lambda x: x.display_name)
                        for account in month_move_lines_credits_accts:
                            debit = sum(month_move_lines_credits.filtered(
                                lambda x: x.account_id == account and x.debit > 0).mapped('secondary_balance'))
                            credit = abs(sum(month_move_lines_credits.filtered(
                                lambda x: x.account_id == account and x.credit < 0).mapped('secondary_balance')))
                            table_line = (
                                account.display_name,
                                '{0:,.0f}'.format(sum(month_move_lines_credits.filtered(
                                    lambda x: x.account_id == account and x.debit > 0).mapped('secondary_balance'))),
                                '{0:,.0f}'.format(abs(sum(month_move_lines_credits.filtered(
                                    lambda x: x.account_id == account and x.credit < 0).mapped('secondary_balance')))),
                            )
                            total_debit += debit
                            total_credit += credit
                            total_gral_debit += debit
                            total_gral_credit += credit
                            TABLE_DATA.append(table_line)
                        TABLE_DATA.append(('Total %s/%s' % (month, year), '{0:,.0f}'.format(
                            total_debit), '{0:,.0f}'.format(total_credit)))
                TABLE_DATA.append(('Total general', '{0:,.0f}'.format(
                    total_gral_debit), '{0:,.0f}'.format(total_gral_credit)))
            pdf = CustomPDF()
            pdf.set_font("Arial", "", 6)
            pdf.start_page_number = self.registration_id.current_number
            pdf.company = self.company_id
            pdf.title = "Libro Diario"
            pdf.subtitle = "Del: %s al %s" % (self.start_date.strftime(
                '%d/%m/%Y'), self.end_date.strftime('%d/%m/%Y'))
            if self.registration_id.signature_image:
                pdf.signature_image = base64.b64decode(
                    self.registration_id.signature_image)
            if self.registration_id.signature_image:
                pdf.signature_image = base64.b64decode(
                    self.registration_id.signature_image)
            pdf.add_page()

            TABLE_DATA = self.format_table_data(TABLE_DATA)

            with pdf.table(col_widths=(70, 15, 15)) as table:
                for ir, data_row in enumerate(TABLE_DATA):
                    row = table.row()
                    for ic, datum in enumerate(data_row):
                        if ic > 0:
                            row.cell(text=datum, align='R')
                        else:
                            row.cell(datum)

            pdf_bytes = None
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                pdf.output(tmp_file.name)

                with open(tmp_file.name, "rb") as file:
                    pdf_bytes = file.read()
                    self.page_quantity = PyPDF2.PdfFileReader(file).numPages

            os.remove(tmp_file.name)
            pdf_base64 = base64.b64encode(pdf_bytes)
            self.report_file_name = "Libro_diario_resumido.pdf"

            self.write({
                'report_file': pdf_base64
            })
        else:
            return super(BookRegistrationReport, self).daily_month_summary_pdf()

    def daily_summary_pdf(self):
         # Override computation to reflect the amounts according to secondary balance
        company = self.env.company
        # Check if the company has a secondary currency set to PYG and is located in PY
        if company.sec_currency_id and company.sec_currency_id.name == "PYG" and company.country_code == "PY":
            TABLE_DATA = [('Cuenta', 'Débito', 'Crédito')]
            moves = self.env['account.move'].search(
                [('date', '>=', self.start_date), ('date', '<=', self.end_date), ('state', '=', 'posted')])

            if moves:
                years = set(moves.sorted(key=lambda x: x.date).mapped(
                    lambda x: x.date.year))
                months = set(moves.sorted(key=lambda x: x.date).mapped(
                    lambda x: x.date.month))
                days = set(moves.sorted(key=lambda x: x.date).mapped(
                    lambda x: x.date.day))
                moves = moves.sorted(key=lambda x: (x.date, x.id))
                total_gral_debit = 0
                total_gral_credit = 0
                for year in years:
                    for month in months:
                        for day in days:
                            total_debit = 0
                            total_credit = 0
                            TABLE_DATA.append(('Fecha: %s/%s/%s' %
                                            (day, month, year), '', ''))
                            day_moves = moves.filtered(
                                lambda x: x.date.month == month and x.date.year == year and x.date.day == day)
                            day_move_lines_debits = day_moves.mapped(
                                'line_ids').filtered(lambda x: x.debit > 0)
                            day_move_lines_debits_accts = sorted(list(
                                set(day_move_lines_debits.mapped('account_id'))), key=lambda x: x.display_name)
                            for account in day_move_lines_debits_accts:
                                debit = sum(day_move_lines_debits.filtered(
                                    lambda x: x.account_id == account and x.debit > 0).mapped('secondary_balance'))
                                credit = abs(sum(day_move_lines_debits.filtered(
                                    lambda x: x.account_id == account and x.credit < 0).mapped('secondary_balance')))
                                table_line = (
                                    account.display_name,
                                    '{0:,.0f}'.format(debit),
                                    '{0:,.0f}'.format(credit),
                                )
                                total_debit += debit
                                total_credit += credit
                                total_gral_debit += debit
                                total_gral_credit += credit
                                TABLE_DATA.append(table_line)
                            day_move_lines_credits = day_moves.mapped(
                                'line_ids').filtered(lambda x: x.credit > 0)
                            day_move_lines_credits_accts = sorted(list(
                                set(day_move_lines_credits.mapped('account_id'))), key=lambda x: x.display_name)
                            for account in day_move_lines_credits_accts:
                                debit = sum(day_move_lines_credits.filtered(
                                    lambda x: x.account_id == account and x.debit > 0).mapped('secondary_balance'))
                                credit = abs(sum(day_move_lines_credits.filtered(
                                    lambda x: x.account_id == account and x.credit < 0).mapped('secondary_balance')))
                                table_line = (
                                    account.display_name,
                                    '{0:,.0f}'.format(sum(day_move_lines_credits.filtered(
                                        lambda x: x.account_id == account and x.debit > 0).mapped('secondary_balance'))),
                                    '{0:,.0f}'.format(sum(day_move_lines_credits.filtered(
                                        lambda x: x.account_id == account and x.credit < 0).mapped('secondary_balance'))),
                                )
                                total_debit += debit
                                total_credit += credit
                                total_gral_debit += debit
                                total_gral_credit += credit
                                TABLE_DATA.append(table_line)
                            TABLE_DATA.append(('Total %s/%s/%s' % (day, month, year), '{0:,.0f}'.format(
                                total_debit), '{0:,.0f}'.format(total_credit)))
                TABLE_DATA.append(('Total general', '{0:,.0f}'.format(
                    total_gral_debit), '{0:,.0f}'.format(total_gral_credit)))

            pdf = CustomPDF()
            pdf.set_font("Arial", "", 6)
            pdf.start_page_number = self.registration_id.current_number
            pdf.company = self.company_id
            pdf.title = "Libro Diario"
            pdf.subtitle = "Del: %s al %s" % (self.start_date.strftime(
                '%d/%m/%Y'), self.end_date.strftime('%d/%m/%Y'))
            if self.registration_id.signature_image:
                pdf.signature_image = base64.b64decode(
                    self.registration_id.signature_image)
            if self.registration_id.signature_image:
                pdf.signature_image = base64.b64decode(
                    self.registration_id.signature_image)
            pdf.add_page()

            TABLE_DATA = self.format_table_data(TABLE_DATA)

            with pdf.table(col_widths=(70, 15, 15)) as table:
                for ir, data_row in enumerate(TABLE_DATA):
                    row = table.row()
                    for ic, datum in enumerate(data_row):
                        if ic > 0:
                            row.cell(text=datum, align='R')
                        else:
                            row.cell(datum)

            pdf_bytes = None
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                pdf.output(tmp_file.name)

                with open(tmp_file.name, "rb") as file:
                    pdf_bytes = file.read()
                    self.page_quantity = PyPDF2.PdfFileReader(file).numPages

            os.remove(tmp_file.name)
            pdf_base64 = base64.b64encode(pdf_bytes)
            self.report_file_name = "Libro_diario_resumido.pdf"
            self.write({
                'report_file': pdf_base64
            })
        else:
            return super(BookRegistrationReport, self).daily_summary_pdf()