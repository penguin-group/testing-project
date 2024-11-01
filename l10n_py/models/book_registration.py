# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import PyPDF2
import os
import tempfile
import base64
from fpdf import FPDF
from werkzeug.urls import url_encode, url_join
from odoo.tools.misc import format_date, DEFAULT_SERVER_DATE_FORMAT
import logging

_logger = logging.getLogger(__name__)

characters_to_replace = ['\u200b', '\u201c']


def remove_unwanted_characters(value):
    allowed_characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÁÉÍÓÚÑáéíóúñ 0123456789~!@#$%^&*()-=[]\;,./_+{}|:<>?'
    for value_character in value:
        if value_character not in allowed_characters:
            value = value.replace(value_character, ' ')
    return value


def format_number_to_string(number):
    if number == '':
        return ''
    return '{0:,.0f}'.format(int(number)).replace(',', '.')


def clean_string(string):
    allowed_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ .,1234567890!@#$%^&*()'
    return string


class BookRegistration(models.Model):
    _name = 'book.registration'
    _description = 'Book Registration'

    name = fields.Char(string="Name")
    initial_number = fields.Integer(string="Initial Number")
    final_number = fields.Integer(string="Final Number")
    current_number = fields.Integer(string="Current Number")
    signature_image = fields.Binary(string="Signature Image")
    company_id = fields.Many2one('res.company', string="Company")
    active = fields.Boolean(string="Active")
    type = fields.Selection(string="Type", selection=[
        ('purchase', 'Purchase Book'),
        ('sale', 'Sale Book'),
        ('daily', 'Daily Book'),
        ('general', 'General Ledger'),
        ('inventory', 'Inventory Book')
    ])


class BookRegistrationReport(models.Model):
    _name = 'book.registration.report'
    _description = 'Book Registration Report'

    name = fields.Char(string="Name")
    page_quantity = fields.Integer(string="Page Quantity")
    registration_id = fields.Many2one(
        'book.registration',
        string="Book Registration",
        domain="[('active','=', True),('company_id','=',company_id)]"
    )
    report_file = fields.Binary(string="Report File")
    report_file_name = fields.Char(string="Report File Name")
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company)
    active = fields.Boolean(string="Active")
    detailed = fields.Boolean(string="Detailed Report")
    type = fields.Selection(string="Type", selection=[
        ('purchase', 'Purchase Book'),
        ('sale', 'Sale Book'),
        ('daily', 'Daily Book'),
        ('daily_month_summary', 'Daily Book Summarized - Monthly'),
        ('daily_summary', 'Daily Book Summarized - Daily'),
        ('general', 'General Ledger'),
        ('inventory', 'Inventory Book')
    ])
    state = fields.Selection(string="State", selection=[
        ('draft', 'Draft'),
        ('printed', 'Printed'),
        ('cancel', 'Cancelled'),
    ], default='draft')
    current_registration_number = fields.Integer(string="Current Number")
    initial_registration_number = fields.Integer(string="Initial Number")
    final_registration_number = fields.Integer(string="Final Number")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")

    @api.onchange('registration_id')
    @api.depends('registration_id')
    def test_onchange(self):
        for record in self:
            record.current_registration_number = self.registration_id.current_number
            record.initial_registration_number = self.registration_id.initial_number
            record.final_registration_number = self.registration_id.final_number

    @api.model
    def create(self, vals):
        res = super(BookRegistrationReport, self).create(vals)
        res.name = "{0} - {1}".format(res.type, fields.Date.today())
        return res

    def download_pdf(self):

        if not self.report_file:
            raise UserError(_("Please generate the file before printing."))

        if self.final_registration_number < self.current_registration_number + self.page_quantity:
            raise UserError(
                _("The number of pages exceeds the maximum available number."))

        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        download_url = url_join(base_url, '/binary/download')

        params = {
            'record_id': self.id,
        }
        query_string = url_encode(params)

        complete_url = "{}?{}".format(download_url, query_string)

        self.state = 'printed'
        self.registration_id.current_number += self.page_quantity

        return {
            'type': 'ir.actions.act_url',
            'url': complete_url,
            'target': 'new',
        }

    def cancel_book_registration(self):
        current_number = self.registration_id.current_number
        if current_number != self.current_registration_number + self.page_quantity:
            raise UserError(
                _("The document cannot be canceled; it does not correspond to the last sequence."))

        self.registration_id.current_number -= self.page_quantity
        self.state = 'cancel'

    def reset_form(self):
        self.report_file = False
        self.state = 'draft'

    def format_table_data(self, table_data):
        table_data = [[remove_unwanted_characters(
            cell) for cell in sublist] for sublist in table_data]
        return table_data

    def generate_pdf(self):
        if self.type == 'daily':
            self.daily_book_pdf()

        if self.type == 'daily_month_summary':
            try:
                self.daily_month_summary_pdf()
            except Exception as ex:
                _logger.error(ex)
                raise UserError(_("Error generating PDF."))

        if self.type == 'daily_summary':
            try:
                self.daily_summary_pdf()
            except Exception as ex:
                _logger.error(ex)
                raise UserError(_("Error generating PDF."))

        if self.type == 'general':
            self.general_ledger_pdf()

        if self.type == 'purchase':
            try:
                self.purchase_sale_pdf(type='purchase')
            except:
                raise UserError(_("Error generating PDF."))
            self.purchase_sale_pdf(type='purchase')

        if self.type == 'sale':
            try:
                self.purchase_sale_pdf(type='sale')
            except:
                raise UserError(_("Error generating PDF."))

        if self.type == 'inventario':
            self.inventory_pdf()

    def purchase_sale_pdf(self, type=None):
        invoices = []
        if type == 'purchase':
            invoices = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'),
                ('state', 'in', ['posted']),
                ('invoice_date', '>=', self.start_date),
                ('invoice_date', '<=', self.end_date),
                ('line_ids.tax_ids', '!=', False),
                ('company_id', '=', self.company_id.id)
            ])
            TABLE_DATA_INVOICES = [(
                'Nro',
                'Fecha',
                'Proveedor',
                'RUC',
                'Tipo doc',
                'Timbrado',
                'Nro Doc',
                "Gravadas 10%",  # "Importe Gravadas 10%",
                "IVA 10%",  # "Debito fiscal 10%",
                "Gravadas 5%",  # "Importe Gravadas 5%",
                "IVA 5%",  # "Debito fiscal 5%",
                "Exentas",  # "Importes Exentas",
                "Total"  # "Importe total facturado con IVA incluido",
            )]

        if type == 'sale':
            invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('state', 'in', ['posted', 'cancel']),
                ('invoice_date', '>=', self.start_date),
                ('invoice_date', '<=', self.end_date),
                ('company_id', '=', self.company_id.id)
            ])

            TABLE_DATA_INVOICES = [(
                'Nro',
                'Fecha',
                'Cliente',
                'RUC',
                'Tipo doc',
                'Nro Doc',
                "Gravadas 10%",  # "Importe Gravadas 10%",
                "IVA 10%",  # "Debito fiscal 10%",
                "Gravadas 5%",  # "Importe Gravadas 5%",
                "IVA 5%",  # "Debito fiscal 5%",
                "Exentas",  # "Importes Exentas",
                "Total"  # "Importe total facturado con IVA incluido",
            )]

        pdf = CustomPDF()
        pdf.start_page_number = self.registration_id.current_number
        pdf.company = self.company_id
        title = """
        Libro {0} - Ley 125/91 Periodo: Del {1} al {2}
        """.format(type, self.start_date.strftime('%d/%m/%Y'), self.end_date.strftime('%d/%m/%Y'))
        pdf.title = title
        if self.registration_id.signature_image:
            pdf.signature_image = base64.b64decode(
                self.registration_id.signature_image)

        pdf.set_font("Arial", "B", 10)
        pdf.add_page()
        pdf.cell(0, 6, "", align="L", ln=True)

        cnt = 0
        total_gral_total = 0
        total_gral_base10 = 0
        total_gral_base5 = 0
        total_gral_vat10 = 0
        total_gral_vat5 = 0
        total_gral_exempt = 0
        for i in invoices.sorted(key=lambda r: r.invoice_date):
            a = 1
            cnt += 1
            total_invoice = 0
            if i.state != 'cancel':
                total_invoice = abs(i.amount_total_signed)
            base10 = 0
            base5 = 0
            exempt = 0
            vat10 = 0
            vat5 = 0

            for t in i.filtered(lambda x: x.state != 'cancel').invoice_line_ids:
                if t.tax_ids and t.tax_ids[0].amount == 10:
                    base10 += t.price_total / 1.1
                    vat10 += t.price_total / 11
                if t.tax_ids and t.tax_ids[0].amount == 5:
                    base5 += t.price_total / 1.05
                    vat5 += t.price_total / 21
                if (t.tax_ids and t.tax_ids[0].amount == 0) or not t.tax_ids:
                    exempt += t.price_total

            if i.currency_id != self.company_id.currency_id:
                base10 = i.currency_id._convert(
                    base10, self.company_id.currency_id, self.company_id, i.invoice_date)
                vat10 = i.currency_id._convert(
                    vat10, self.company_id.currency_id, self.company_id, i.invoice_date)
                base5 = i.currency_id._convert(
                    base5, self.company_id.currency_id, self.company_id, i.invoice_date)
                vat5 = i.currency_id._convert(
                    vat5, self.company_id.currency_id, self.company_id, i.invoice_date)
                exempt = i.currency_id._convert(
                    exempt, self.company_id.currency_id, self.company_id, i.invoice_date)

            total_gral_total += total_invoice
            total_gral_base10 += base10
            total_gral_base5 += base5
            total_gral_vat10 += vat10
            total_gral_vat5 += vat5
            total_gral_exempt += exempt

            def _get_type_doc(invo):
                type = "Anulado"
                if invo.state != 'cancel':
                    if invo.invoice_date < invo.invoice_date_due:
                        type = "Credito"
                    else:
                        type = "Contado"
                return type

            if type == 'purchase':
                TABLE_DATA_INVOICES.append([
                    str(cnt),
                    str(i.invoice_date.strftime("%d/%m/%y")),
                    str(i.partner_id.name),
                    str(i.partner_id.vat),
                    _get_type_doc(i),
                    str(i.supplier_invoice_authorization_id.name) if i.supplier_invoice_authorization_id else ' ',
                    str(i.ref) if i.ref else '',

                    '{0:,.0f}'.format(int(base10)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(vat10)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(base5)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(vat5)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(exempt)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(total_invoice)).replace(
                        ',', '.') if i.state != 'cancel' else "0"
                ])
            else:
                TABLE_DATA_INVOICES.append([
                    str(cnt),
                    str(i.invoice_date.strftime("%d/%m/%y")),
                    str(i.partner_id.name),
                    str(i.partner_id.vat),
                    _get_type_doc(i),
                    str(i.name),

                    '{0:,.0f}'.format(int(base10)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(vat10)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(base5)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(vat5)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(exempt)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(total_invoice)).replace(
                        ',', '.') if i.state != 'cancel' else "0"
                ])

        if type == 'purchase':
            TABLE_DATA_INVOICES.append([' ', ' ', 'Total', ' ', ' ', ' ', ' ',
                                        '{0:,.0f}'.format(
                                            int(total_gral_base10)).replace(',', '.'),
                                        '{0:,.0f}'.format(
                                            int(total_gral_vat10)).replace(',', '.'),
                                        '{0:,.0f}'.format(
                                            int(total_gral_base5)).replace(',', '.'),
                                        '{0:,.0f}'.format(
                                            int(total_gral_vat5)).replace(',', '.'),
                                        '{0:,.0f}'.format(
                                            int(total_gral_exempt)).replace(',', '.'),
                                        '{0:,.0f}'.format(
                                            int(total_gral_total)).replace(',', '.')
                                        ])

        if type == 'sale':
            TABLE_DATA_INVOICES.append([' ', ' ', 'Total', ' ', ' ', ' ',
                                        '{0:,.0f}'.format(
                                            int(total_gral_base10)).replace(',', '.'),
                                        '{0:,.0f}'.format(
                                            int(total_gral_vat10)).replace(',', '.'),
                                        '{0:,.0f}'.format(
                                            int(total_gral_base5)).replace(',', '.'),
                                        '{0:,.0f}'.format(
                                            int(total_gral_vat5)).replace(',', '.'),
                                        '{0:,.0f}'.format(
                                            int(total_gral_exempt)).replace(',', '.'),
                                        '{0:,.0f}'.format(
                                            int(total_gral_total)).replace(',', '.')
                                        ])

        pdf.set_font("Arial", "", 6)
        if type == 'purchase':
            widths = (5, 8, 20, 10, 9, 10, 15, 10, 10, 10, 10, 10, 10)
        if type == 'sale':
            widths = (5, 8, 20, 10, 9, 15, 10, 10, 10, 10, 10, 10)
        with pdf.table(col_widths=widths) as table_invoices:
            for ir, data_row in enumerate(TABLE_DATA_INVOICES):
                row = table_invoices.row()
                for ic, datum in enumerate(data_row):
                    if ic > 5 and ir > 0:
                        row.cell(text=datum, align='R')
                    else:
                        row.cell(datum)

        credit_notes = []
        if type == 'purchase':
            credit_notes = self.env['account.move'].search([
                ('move_type', '=', 'out_refund'),
                ('state', 'in', ['posted', 'cancel']),
                ('invoice_date', '>=', self.start_date),
                ('invoice_date', '<=', self.end_date),
                ('line_ids.tax_ids', '!=', False),
                ('company_id', '=', self.company_id.id)
            ])
            TABLE_DATA_CREDIT_NOTES = [(
                'Nro',
                'Fecha',
                'Cliente',
                'RUC',
                'Tipo doc',
                'Nro Doc',
                "Gravadas 10%",  # "Importe Gravadas 10%",
                "IVA 10%",  # "Debito fiscal 10%",
                "Gravadas 5%",  # "Importe Gravadas 5%",
                "IVA 5%",  # "Debito fiscal 5%",
                "Exentas",  # "Importes Exentas",
                "Total"  # "Importe total facturado con IVA incluido",
            )]

        if type == 'sale':
            credit_notes = self.env['account.move'].search([
                ('move_type', '=', 'in_refund'),
                ('state', 'in', ['posted']),
                ('invoice_date', '>=', self.start_date),
                ('invoice_date', '<=', self.end_date),
                ('company_id', '=', self.company_id.id)
            ])

            TABLE_DATA_CREDIT_NOTES = [(
                'Nro',
                'Fecha',
                'Proveedor',
                'RUC',
                'Tipo doc',
                'Timbrado',
                'Nro Doc',
                "Gravadas 10%",  # "Importe Gravadas 10%",
                "IVA 10%",  # "Debito fiscal 10%",
                "Gravadas 5%",  # "Importe Gravadas 5%",
                "IVA 5%",  # "Debito fiscal 5%",
                "Exentas",  # "Importes Exentas",
                "Total"  # "Importe total facturado con IVA incluido",
            )]

        pdf.set_font("Arial", "B", 10)
        if type == 'purchase':
            pdf.cell(0, 5, "Notas de crédito emitidas", align="L", ln=True)
        if type == 'sale':
            pdf.cell(0, 5, "Notas de crédito recibidas", align="L", ln=True)
        pdf.cell(0, 5, "", align="L", ln=True)

        cnt = 0
        total_gral_total = 0
        total_gral_base10 = 0
        total_gral_base5 = 0
        total_gral_vat10 = 0
        total_gral_vat5 = 0
        total_gral_exempt = 0
        for i in credit_notes.sorted(key=lambda x: x.invoice_date):
            cnt += 1
            total_invoice = 0
            if i.state != 'cancel':
                total_invoice = i.amount_total
            base10 = 0
            base5 = 0
            exempt = 0
            vat10 = 0
            vat5 = 0
            for t in i.filtered(lambda x: x.state != 'cancel').invoice_line_ids:
                if t.tax_ids and t.tax_ids[0].amount == 10:
                    base10 += t.price_total / 1.1
                    vat10 += t.price_total / 11
                if t.tax_ids and t.tax_ids[0].amount == 5:
                    base5 += t.price_total / 1.05
                    vat5 += t.price_total / 21
                if (t.tax_ids and t.tax_ids[0].amount == 0) or not t.tax_ids:
                    exempt += t.price_total

            if i.currency_id != self.company_id.currency_id:
                base10 = i.currency_id._convert(
                    base10, self.company_id.currency_id, self.company_id, i.invoice_date)
                vat10 = i.currency_id._convert(
                    vat10, self.company_id.currency_id, self.company_id, i.invoice_date)
                base5 = i.currency_id._convert(
                    base5, self.company_id.currency_id, self.company_id, i.invoice_date)
                vat5 = i.currency_id._convert(
                    vat5, self.company_id.currency_id, self.company_id, i.invoice_date)
                exempt = i.currency_id._convert(
                    exempt, self.company_id.currency_id, self.company_id, i.invoice_date)
                total_invoice = i.currency_id._convert(
                    total_invoice, self.company_id.currency_id, self.company_id, i.invoice_date)

            total_gral_total += total_invoice
            total_gral_base10 += base10
            total_gral_base5 += base5
            total_gral_vat10 += vat10
            total_gral_vat5 += vat5
            total_gral_exempt += exempt

            def _get_type_doc(invoice):
                type = " "
                if invoice.state != 'cancel':
                    type = "Nota crédito"
                return type

            if type == 'purchase':
                TABLE_DATA_CREDIT_NOTES.append([
                    str(cnt),
                    str(i.invoice_date.strftime("%d/%m/%y")),
                    str(i.partner_id.name).strip(),
                    str(i.partner_id.vat).strip(),
                    _get_type_doc(i),
                    str(i.name),
                    '{0:,.0f}'.format(int(base10)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(vat10)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(base5)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(vat5)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(exempt)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(total_invoice)).replace(
                        ',', '.') if i.state != 'cancel' else "0"
                ])

            if type == 'sale':
                TABLE_DATA_CREDIT_NOTES.append([
                    str(cnt),
                    str(i.invoice_date.strftime("%d/%m/%y")),
                    str(i.partner_id.name).strip(),
                    str(i.partner_id.vat).strip(),
                    _get_type_doc(i),
                    i.supplier_invoice_authorization_id.name if i.supplier_invoice_authorization_id else ' ',
                    str(i.ref),
                    '{0:,.0f}'.format(int(base10)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(vat10)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(base5)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(vat5)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(exempt)).replace(
                        ',', '.') if i.state != 'cancel' else "0",
                    '{0:,.0f}'.format(int(total_invoice)).replace(
                        ',', '.') if i.state != 'cancel' else "0"
                ])

        if type == 'sale':
            TABLE_DATA_CREDIT_NOTES.append([' ', ' ', 'Total', ' ', ' ', ' ', ' ',
                                            '{0:,.0f}'.format(
                                                int(total_gral_base10)).replace(',', '.'),
                                            '{0:,.0f}'.format(
                                                int(total_gral_vat10)).replace(',', '.'),
                                            '{0:,.0f}'.format(
                                                int(total_gral_base5)).replace(',', '.'),
                                            '{0:,.0f}'.format(
                                                int(total_gral_vat5)).replace(',', '.'),
                                            '{0:,.0f}'.format(
                                                int(total_gral_exempt)).replace(',', '.'),
                                            '{0:,.0f}'.format(
                                                int(total_gral_total)).replace(',', '.')
                                            ])

        if type == 'purchase':
            TABLE_DATA_CREDIT_NOTES.append([' ', ' ', 'Total', ' ', ' ', ' ',
                                            '{0:,.0f}'.format(
                                                int(total_gral_base10)).replace(',', '.'),
                                            '{0:,.0f}'.format(
                                                int(total_gral_vat10)).replace(',', '.'),
                                            '{0:,.0f}'.format(
                                                int(total_gral_base5)).replace(',', '.'),
                                            '{0:,.0f}'.format(
                                                int(total_gral_vat5)).replace(',', '.'),
                                            '{0:,.0f}'.format(
                                                int(total_gral_exempt)).replace(',', '.'),
                                            '{0:,.0f}'.format(
                                                int(total_gral_total)).replace(',', '.')
                                            ])
        pdf.set_font("Arial", "", 6)

        if type == 'sale':
            widths = (5, 8, 20, 10, 9, 10, 15, 10, 10, 10, 10, 10, 10)
        if type == 'purchase':
            widths = (5, 8, 20, 10, 9, 15, 10, 10, 10, 10, 10, 10)
        with pdf.table(col_widths=widths) as table_credit_notes:
            for ir, data_row in enumerate(TABLE_DATA_CREDIT_NOTES):
                row = table_credit_notes.row()
                for ic, datum in enumerate(data_row):
                    if ic > 5 and ir > 0:
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
        self.report_file_name = "Libro_{0}.pdf".format(type)
        self.write({
            'report_file': pdf_base64
        })

    def general_ledger_pdf(self):
        invoices = self.env['account.move.line'].search([
            ('parent_state', 'in', ['posted']),
            ('date', '<=', self.end_date),
            ('company_id', '=', self.company_id.id)
        ], order=('id'))
        pdf = CustomPDF()
        pdf.set_font("Arial", "", 5)
        pdf.start_page_number = self.registration_id.current_number
        pdf.company = self.company_id
        pdf.title = "Libro Mayor - Periodo: Del {0} al {1}".format(
            self.start_date.strftime('%d/%m/%Y'), self.end_date.strftime('%d/%m/%Y'))
        if self.registration_id.signature_image:
            pdf.signature_image = base64.b64decode(
                self.registration_id.signature_image)
        pdf.add_page()
        if not self.detailed:
            query = f"""
                select ml.account_id as r_account_id, aa.name as r_account_name, sum(ml.debit) as debit,
                sum(ml.credit) as credit, sum(ml.balance) as balance, aa.code as code
                FROM public.account_move_line as ml inner join account_account as aa on ml.account_id = aa.id
                where ml.date <= '{self.end_date}' and ml.company_id = '{self.company_id.id}' and ml.parent_state = 'posted'
                group by ml.account_id, aa.name, aa.code order by ml.account_id, aa.code

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
                r_account_id, r_account_name, debit, credit, balance, code = row

                debit = int(debit)
                credit = int(credit)
                balance = int(balance)
                total_debit_t = debit
                total_credit_t = credit
                total_balance_t = balance
                TABLE_DATA.append([
                    str(code) + ' - ' +
                    str(r_account_name).replace('₲', '').strip(),  # Account
                    '{0:,.0f}'.format(int(debit)).replace(',', '.'),  # Debit
                    '{0:,.0f}'.format(int(credit)).replace(',', '.'),  # Credit
                    '{0:,.0f}'.format(int(balance)).replace(
                        ',', '.')  # Balance

                ])
                total_debit += total_debit_t
                total_credit += total_credit_t
                total_balance += total_balance_t

            TABLE_DATA.append(['',
                               '{0:,.0f}'.format(
                                   int(total_debit)).replace(',', '.'),
                               '{0:,.0f}'.format(
                                   int(total_credit)).replace(',', '.'),
                               '{0:,.0f}'.format(
                                   int(total_balance)).replace(',', '.'),
                               ])

            TABLE_DATA = self.format_table_data(TABLE_DATA)

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
                'Nro Asiento',
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
                            SUM(ml.debit) AS debit_total,
                            SUM(ml.credit) AS credit_total,
                            SUM(ml.balance) AS balance_total
                        FROM
                            public.account_move_line AS ml
                        WHERE
                            ml.date < '{self.start_date}' -- Deadline for previous dates
                            AND ml.company_id = '{self.company_id.id}'
                            and ml.parent_state = 'posted'
                        GROUP BY
                            ml.account_id
                    )
                    SELECT
                        am.journal_entry_number as journal_entry_number,
                        ml.date as date,
                        ml.account_id AS r_account_id,
                        aa.name as r_account_name,
                        ml.name as account_line_name,
                        ml.debit as debit,
                        ml.credit as credit,
                        ml.balance as balance,
                        sub.debit_total as debit_total,
                        sub.credit_total as credit_total,
                        sub.balance_total as balance_total,
                        aa.id as account_code,
                        am.name as reference,
                        aa.code as code,
                        CASE
                            WHEN aa.name IS NOT NULL THEN 'Dentro del Rango'
                        END as query_state,
                        ml.id as line_code

                    FROM
                        public.account_move_line AS ml
                    INNER JOIN
                        account_account AS aa ON ml.account_id = aa.id
                    inner
                        join account_move as am on ml.move_id = am.id
                    LEFT JOIN
                        subquery as sub ON ml.account_id = sub.account_id
                    WHERE
                        ml.date >= '{self.start_date}'
                        AND ml.date <= '{self.end_date}'
                        AND ml.company_id = '{self.company_id.id}'
                        and ml.parent_state = 'posted'
                    GROUP BY
                        journal_entry_number,ml.date, ml.account_id, aa.name, ml.name,sub.debit_total, sub.credit_total,sub.balance_total,
                        ml.debit,ml.credit,ml.balance,aa.id, am.name,aa.code, ml.id

                UNION

                    SELECT
                        NULL as journal_entry_number,
                        NULL as date,
                        ml.account_id,
                        aa.name as r_account_name,
                        Null as account_line_name,
                        0 as debit,
                        0 as credit,
                        0 as balance,
                        SUM(ml.debit) AS debit_total,
                        SUM(ml.credit) AS credit_total,
                        SUM(ml.balance) AS balance_total,
                        aa.id as account_code,
                        NULL as reference,
                        aa.code as code,
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
                        ml.account_id, aa.name, aa.code, aa.id


                ORDER BY
                    ---ml.account_id, ml.date,aa.code
                    code, journal_entry_number
                    ---, date DESC;

            """

            self.env.cr.execute(query)
            results = self.env.cr.fetchall()
            account_name_group = []

            for row in results:
                journal_entry_number, date, r_account_id, r_account_name, account_line_name, debit, credit, balance, debit_total, credit_total, total_balance, account_code, reference, code, query_state, line_code = row
                if r_account_id not in [item['account'] for item in account_name_group]:
                    a = {
                        'account': r_account_id,
                        'r_account_name': r_account_name,
                        'debit_total': (debit_total),
                        'credit_total': (credit_total),
                        'balance_total': (total_balance),
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
                    total_balance = 0
                else:
                    total_balance = item['balance_total']

                balance_total_balance = total_balance

                TABLE_DATA.append([
                    '',
                    '',
                    str(item['code']) + ' - ' + str(item['r_account_name']
                                                    # Account
                                                    ).replace('₲', '').strip(),
                    '',
                    '',
                    '',
                    '',

                ])
                TABLE_DATA.append([
                    '',
                    '',
                    'Saldo inicial',
                    '',
                    '{0:,.0f}'.format(int(debit_total)).replace(',', '.'),
                    '{0:,.0f}'.format(int(credit_total)).replace(',', '.'),
                    '{0:,.0f}'.format(int(total_balance)).replace(',', '.'),

                ])
                reference_balance_computation = 0
                cnt = 0
                for row in results:
                    journal_entry_number, date, r_account_id, r_account_name, account_line_name, debit, credit, balance, debit_total, credit_total, total_balance, account_code, reference, code, query_state, line_code = row
                    if item['query_state'] == 'Dentro del Rango':
                        if r_account_id == item['account']:
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
                                reference_balance_computation = (
                                    c + debit) - credit

                            TABLE_DATA.append([
                                '{0:,.0f}'.format(
                                    int(journal_entry_number)).replace(',', '.'),
                                date,
                                '',
                                reference,
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
                        total_debit_total_inicial_balance = debit_total_balance + total_debit

                    elif debit_total_balance > 0 and total_debit == 0:
                        total_debit_total_inicial_balance = debit_total_balance

                    else:
                        total_debit_total_inicial_balance = total_debit
                    # Credit
                    if credit_total_balance > 0 and total_credit > 0:
                        total_credit_total_inicial_balance = credit_total_balance + total_credit

                    elif credit_total_balance > 0 and total_credit == 0:
                        total_credit_total_inicial_balance = credit_total_balance

                    else:
                        total_credit_total_inicial_balance = total_credit

                    # Saldo
                    if balance_total_balance != 0 and total_balance != 0:
                        total_balance_total_inicial_balance = balance_total_balance + total_balance
                    else:
                        total_balance_total_inicial_balance = total_balance

                    TABLE_DATA.append([
                        ' ',
                        ' ',
                        'Total ' + str(item['code']) + ' - ' + str(
                            # Account
                            item['r_account_name']).replace('₲', '').strip(),
                        ' ',
                        '{0:,.0f}'.format(
                            int(total_debit_total_inicial_balance)).replace(',', '.'),
                        '{0:,.0f}'.format(
                            int(total_credit_total_inicial_balance)).replace(',', '.'),
                        '{0:,.0f}'.format(
                            int(total_balance_total_inicial_balance)).replace(',', '.'),
                    ])
                else:
                    TABLE_DATA.append([
                        ' ',
                        ' ',
                        'Total ' + str(item['code']) + ' - ' + str(
                            # Account
                            item['r_account_name']).replace('₲', '').strip(),
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
                ' ',
                '{0:,.0f}'.format(int(result_debit)).replace(',', '.'),
                '{0:,.0f}'.format(int(result_credit)).replace(',', '.'),
                '{0:,.0f}'.format(int(result_balance)).replace(',', '.'),
            ])

            TABLE_DATA = self.format_table_data(TABLE_DATA)

            with pdf.table(col_widths=(10, 10, 50, 50, 15, 15, 15)) as table:
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

    def daily_book_pdf(self):
        TABLE_DATA = [
            ('Cuenta', 'Descripción', 'Detalle', 'Crédito', 'Débito')]
        moves = self.env['account.move'].search(
            [('date', '>=', self.start_date), ('date', '<=', self.end_date), ('state', '=', 'posted')])
        if moves:
            moves = list(moves)
            moves.reverse()
        for move in moves:
            TABLE_DATA.append(('Asiento:{0} Fecha: {1}'.format(str(move.journal_entry_number).strip(
            ), str(move.date.strftime('%d/%m/%Y')).strip()), '', '', '', ''))

            for line in move.line_ids:
                table_line = (
                    str(line.account_id.display_name if line.account_id.display_name else ' ').replace(
                        '₲', '').strip(),
                    str(line.name if line.name else ' ').replace(
                        '₲', '').strip(),
                    str(line.ref if line.ref else ' ').replace('₲', '').strip(),
                    '{0:,.0f}'.format(int(line.debit)).replace(
                        ',', '.') if line.debit else '0',
                    '{0:,.0f}'.format(int(line.credit)).replace(
                        ',', '.') if line.credit else '0'
                )
                TABLE_DATA.append(table_line)

        TABLE_DATA = self.format_table_data(TABLE_DATA)

        pdf = CustomPDF()
        pdf.set_font("Arial", "", 6)
        pdf.start_page_number = self.registration_id.current_number
        pdf.company = self.company_id
        pdf.title = "Libro Diario"
        if self.registration_id.signature_image:
            pdf.signature_image = base64.b64decode(
                self.registration_id.signature_image)
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

    def daily_month_summary_pdf(self):
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
                            lambda x: x.account_id == account).mapped('debit'))
                        credit = sum(month_move_lines_debits.filtered(
                            lambda x: x.account_id == account).mapped('credit'))
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
                            lambda x: x.account_id == account).mapped('debit'))
                        credit = sum(month_move_lines_credits.filtered(
                            lambda x: x.account_id == account).mapped('credit'))
                        table_line = (
                            account.display_name,
                            '{0:,.0f}'.format(sum(month_move_lines_credits.filtered(
                                lambda x: x.account_id == account).mapped('debit'))),
                            '{0:,.0f}'.format(sum(month_move_lines_credits.filtered(
                                lambda x: x.account_id == account).mapped('credit'))),
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

    def daily_summary_pdf(self):
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
                                lambda x: x.account_id == account).mapped('debit'))
                            credit = sum(day_move_lines_debits.filtered(
                                lambda x: x.account_id == account).mapped('credit'))
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
                                lambda x: x.account_id == account).mapped('debit'))
                            credit = sum(day_move_lines_credits.filtered(
                                lambda x: x.account_id == account).mapped('credit'))
                            table_line = (
                                account.display_name,
                                '{0:,.0f}'.format(sum(day_move_lines_credits.filtered(
                                    lambda x: x.account_id == account).mapped('debit'))),
                                '{0:,.0f}'.format(sum(day_move_lines_credits.filtered(
                                    lambda x: x.account_id == account).mapped('credit'))),
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

    def inventory_pdf(self):
        debug_mode = False
        # The content of this variable will be calculated outside the function that prints the lines;
        # therefore, it is declared as a global variable.
        global expressions_totals

        if self.company_id.show_inventory_book_base_report_bs_details:
            TABLE_DATA_BS = [
                [
                    'Cantidad',
                    'Detalle',
                    'Precio Unitario',
                    'Subtotal',
                    'Total',
                ],
            ]
        else:
            TABLE_DATA_BS = [
                [
                    'Detalle',
                    'Subtotal',
                    'Total',
                ],
            ]

        if debug_mode:
            TABLE_DATA_BS[0] += ['--']
        TABLE_DATA_IS = TABLE_DATA_BS.copy()

        previous_options = {
            'single_company': self.company_id.ids,
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
            'unposted_in_period': False
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
            if self.company_id.show_inventory_book_base_report_bs_details:
                table_line += ['']
            table_line.append(account_id.code + ' - ' + account_id.name)
            if debug_mode:
                table_line.append(show_account_detail_mode)
            if self.company_id.show_inventory_book_base_report_bs_details:
                table_line += ['']
            if self.company_id.show_inventory_book_base_report_bs_details:
                table_line += ['']
            table_line.append(account_id_dict.get('account_total'))
            if not self.company_id.show_inventory_book_base_report_bs_details:
                table_line += ['']
            table_lines.append(table_line)

            if not show_account_detail_mode:
                pass
            elif show_account_detail_mode == 'mode_account_balance':
                table_line = []
                table_line += ['']
                table_line.append('Saldo Conciliado')
                table_line += ['']
                table_line.append(account_id_dict.get('account_balance'))
                table_line += ['']
                table_lines.append(table_line)
                table_line = []

                table_line += ['']
                table_line.append('Pagos pendientes de conciliación')
                table_line += ['']
                table_line.append(account_id_dict.get('pending_outbound'))
                table_line += ['']
                table_lines.append(table_line)
                table_line = []

                table_line += ['']
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
                        table_line += ['']
                        table_line.append(
                            partner_id.name if partner_id else 'Sin nombre')
                        table_line.append(sum(
                            account_move_line.amount_residual for account_move_line in account_move_line_ids_partner))
                        table_line += [''] * 2
                        table_lines.append(table_line)
            elif show_account_detail_mode == 'mode_account_inventory':
                if env.ref('base.module_stock').state in ['installed', 'to upgrade']:
                    stock_valuation_layer_ids = env['stock.valuation.layer'].sudo().search([
                        ('product_id.categ_id.property_stock_valuation_account_id',
                         '=', account_id.id),
                    ])
                    for product_id in stock_valuation_layer_ids.sudo().product_id:
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

                        table_line.append(
                            stock_valuation_layers_product_id_quantity)
                        table_line.append(product_id.name)
                        table_line.append(
                            stock_valuation_layers_product_id_unit_cost)
                        table_line.append(
                            stock_valuation_layers_product_id_value)
                        table_line += ['']
                        table_lines.append(table_line)
            elif show_account_detail_mode == 'mode_account_asset_fixed':
                account_assets = env['account.asset'].search([
                    ('state', 'in', ['open', 'close']),
                    ('account_asset_id', '=', account_id.id),
                ])
                for account_asset in account_assets:
                    table_line = []
                    table_line += ['']
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
                    if self.company_id.show_inventory_book_base_report_bs_details:
                        table_line += ['']
                    table_line.append(
                        account_group_id.code_prefix_start + ' - ' + account_group_id.name)
                    if self.company_id.show_inventory_book_base_report_bs_details:
                        table_line += ['']
                    table_line += ['']
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
            subformula_field = ''
            subformula_field = 'subformula'

            global expressions_totals

            if headers:
                headers = False

            for report_line in report_lines:
                foldable = False
                foldable = report_line.foldable

                expression_ids = False
                expression_ids = report_line.expression_ids
                report_line_total = 0
                if force_print_from_report_totals and \
                        force_report_totals or \
                        (
                            force_report_totals and
                            ('cross_report' in [expression_id[subformula_field] for expression_id in expression_ids]) or
                            (not foldable and not report_line.hide_if_zero)
                        ):
                    if force_report_totals:
                        for clave in force_report_totals:
                            # Check if the key is in the other dictionary.
                            if clave in expression_ids.ids:
                                # Add the corresponding value.
                                report_line_total += force_report_totals[clave]['value']
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

                if hide_empty_lines and not report_line_total and not debug_mode:
                    continue
                table_line = []
                if self.company_id.show_inventory_book_base_report_bs_details:
                    table_line += ['']
                table_line.append(report_line.name)
                if debug_mode:
                    # ONLY PRESENT IN DEBUG MODE
                    table_line.append(report_line.id)
                if self.company_id.show_inventory_book_base_report_bs_details:
                    table_line += ['']
                table_line += ['']
                table_line.append(report_line_total)

                report_line_expressions = []
                report_line_expressions = report_line.expression_ids.filtered(
                    lambda x: x.engine == 'domain')
                # The expressions of the lines that form the report structure are filtered,
                # only the expressions that use 'domain' for the calculation of their content will be used.

                TABLE_DATA.append(table_line)
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
        account_financial_report_bg_l10n_py = self.company_id.inventory_book_base_report_bs
        if not account_financial_report_bg_l10n_py:
            raise ValidationError(_
                                  ('A base report for the Balance Sheet of the Inventory Book report is not set. Please go to the accounting settings to establish the necessary parameters.'))
        account_financial_report_bg_l10n_py_report_informations = False
        account_financial_report_bg_l10n_py_report_informations = account_financial_report_bg_l10n_py.get_report_information(
            previous_options)
        account_financial_report_bg_l10n_py_report_informations = account_financial_report_bg_l10n_py_report_informations.get(
            'column_groups_totals')
        account_financial_report_bg_l10n_py_report_informations = account_financial_report_bg_l10n_py_report_informations.get(
            list(account_financial_report_bg_l10n_py_report_informations.keys())[
                0]
        )

        # All the account values to be printed will go here.
        expressions_totals = {}
        expression_ids = []
        expression_ids = account_financial_report_bg_l10n_py.line_ids.expression_ids.filtered(
            lambda x: x.engine == 'domain')
        # The expressions of the lines that form the report structure are filtered; 
        # only the expressions that use 'domain' for calculating their content will be used.

        for expression_id in expression_ids:
            expressions_totals[expression_id] = {}
            aml_ids = self.env['account.move.line']
            if expression_id.formula:
                aml_ids = eval(
                    "self.env['account.move.line'].search(" + expression_id.formula + ")")
                # Each expression to be processed has a domain to obtain the accounting entries, 
                # from which the accounts to be processed must be obtained.

            aml_ids = aml_ids.search(
                [('id', 'in', aml_ids.ids), ('date', '<=', previous_options['date']['date_to'])])

            account_ids = self.env['account.account']
            if aml_ids:
                self.env.cr.execute(
                    """SELECT account_id FROM account_move_line WHERE id IN %s""" % (
                        "(" + ','.join(str(aml_id) for aml_id in aml_ids.ids)) + ")"
                )
                query_result = self.env.cr.fetchall()
                account_ids = account_ids.browse(
                    list(set([t[0] for t in query_result])))

            account_ids = account_ids.filtered(
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
                )
            ).sorted(key=lambda x: x.code)
            for account_id in account_ids:

                # BALANCE AS OF DATE
                account_move_line_ids = aml_ids.search([
                    ('id', 'in', aml_ids.ids),
                    ('account_id', '=', account_id.id),
                    ('parent_state', '=', 'posted'),
                ])
                if account_move_line_ids:
                    account_balance = sum(
                        account_move_line_ids.mapped('balance'))
                else:
                    account_balance = 0
                account_outbound = 0
                account_inbound = 0
                amount_field = 'amount_company_currency_signed'
                amount_field = 'amount_company_currency_signed'
                for move_type in ['outbound', 'inbound']:
                    self.env.cr.execute("""
                                SELECT SUM(""" + amount_field + """) AS amount_total_company
                                  FROM account_payment payment
                                  JOIN account_move move ON move.payment_id = payment.id
                                 WHERE payment.is_matched IS NOT TRUE
                                   AND payment.payment_type = %s
                                   AND move.state = 'posted'
                                   AND move.journal_id = ANY(%s)
                              GROUP BY move.company_id, move.journal_id, move.currency_id
                            """, [move_type, self.env['account.journal'].search(
                        [('default_account_id', '=', account_id.id)]).ids])  # We must obtain all outstanding balances for the account
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
                account_type = account_id.account_type
                if self.company_id.show_inventory_book_base_report_bs_details:
                    if account_type == 'asset_cash' and not account_id.reconcile:
                        show_account_detail_mode = 'mode_account_balance'

                    elif (account_type == 'asset_receivable' and account_id.reconcile) or \
                            (account_type == 'liability_payable' and account_id.reconcile):
                        show_account_detail_mode = 'mode_account_partners'

                    elif account_type == 'asset_current' and not account_id.reconcile and account_id.create_asset in ['no']:
                        show_account_detail_mode = 'mode_account_inventory'

                    elif (account_type == 'asset_fixed') or \
                            (account_type == 'liability_current') or \
                            (
                        account_type == 'asset_current' and
                        not account_id.reconcile and
                        account_id.create_asset in ['draft', 'validate'] and
                        account_id.asset_model
                    ):
                        show_account_detail_mode = 'mode_account_asset_fixed'
                account_user_type = account_id.user_type_id
                if self.company_id.show_inventory_book_base_report_bs_details:
                    if account_user_type == self.env.ref('account.data_account_type_liquidity') and not account_id.reconcile:
                        show_account_detail_mode = 'mode_account_balance'

                    elif (account_user_type == self.env.ref('account.data_account_type_receivable') and account_id.reconcile) or \
                            (account_user_type == self.env.ref('account.data_account_type_payable') and account_id.reconcile):
                        show_account_detail_mode = 'mode_account_partners'

                    elif account_user_type == self.env.ref(
                            'account.data_account_type_current_assets') and not account_id.reconcile and account_id.create_asset in ['no']:
                        show_account_detail_mode = 'mode_account_inventory'

                    elif (account_user_type == self.env.ref('account.data_account_type_fixed_assets')) or \
                            (account_user_type == self.env.ref('account.data_account_type_current_liabilities')) or \
                            (
                        account_user_type == self.env.ref('account.data_account_type_current_assets') and
                        not account_id.reconcile and
                        account_id.create_asset in ['draft', 'validate'] and
                        account_id.asset_model
                    ):
                        show_account_detail_mode = 'mode_account_asset_fixed'

                subformula = ''
                subformula = expression_id.subformula

                if subformula == '-sum':
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
            report_lines=account_financial_report_bg_l10n_py.line_ids.filtered(
                lambda x: not x.parent_id),
            padding=1,
            headers=True,
            quantity_headers=True,
            hide_empty_lines=True,
            force_print_from_report_totals=False,
            force_report_totals=account_financial_report_bg_l10n_py_report_informations,
            account_report_id=account_financial_report_bg_l10n_py,
        )

        # INCOME STATEMENT

        TABLE_DATA = TABLE_DATA_IS
        account_financial_report_er_l10n_py = self.company_id.inventory_book_base_report_is
        if not account_financial_report_er_l10n_py:
            raise ValidationError(_(
                'A base report for the Income Statement of the Inventory Book report '
                'is not set. Please go to the accounting settings to establish the '
                'necessary parameters.'
            ))
        account_financial_report_er_l10n_py_report_informations = False
        account_financial_report_er_l10n_py_report_informations = account_financial_report_er_l10n_py.get_report_information(
            previous_options)
        account_financial_report_er_l10n_py_report_informations = account_financial_report_er_l10n_py_report_informations.get(
            'column_groups_totals')
        account_financial_report_er_l10n_py_report_informations = account_financial_report_er_l10n_py_report_informations.get(
            list(account_financial_report_er_l10n_py_report_informations.keys())[
                0]
        )

        # All the account values to be printed will go here.
        expressions_totals = {}

        expression_ids = []
        expression_ids = account_financial_report_er_l10n_py.line_ids.expression_ids.filtered(
            lambda x: x.engine == 'domain')
        # The expressions of the lines that form the report structure are filtered;
        # only the expressions that use 'domain' for calculating their content will be used.
        for expression_id in expression_ids:
            expressions_totals[expression_id] = {}
            aml_ids = self.env['account.move.line']
            if expression_id.formula:
                aml_ids = eval(
                    "self.env['account.move.line'].search(" + expression_id.formula + ")")
                # Each expression to be processed has a domain to obtain the accounting entries,
                # from which the accounts to be processed must be obtained.

            aml_ids = aml_ids.search(
                [('id', 'in', aml_ids.ids), ('date', '<=', previous_options['date']['date_to'])])

            account_ids = self.env['account.account']
            if aml_ids:
                self.env.cr.execute(
                    """SELECT account_id FROM account_move_line WHERE id IN %s""" % (
                        "(" + ','.join(str(aml_id) for aml_id in aml_ids.ids)) + ")"
                )
                query_result = self.env.cr.fetchall()
                account_ids = account_ids.browse(
                    list(set([t[0] for t in query_result])))

            account_ids = account_ids.filtered(
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
            ).sorted(key=lambda x: x.code)

            for account_id in account_ids:

                # BALANCE AS OF DATE
                account_move_line_ids = aml_ids.search([
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
                amount_field = 'amount_company_currency_signed'
                amount_field = 'amount_company_currency_signed'
                for move_type in ['outbound', 'inbound']:
                    self.env.cr.execute("""
                                SELECT SUM(""" + amount_field + """) AS amount_total_company
                                  FROM account_payment payment
                                  JOIN account_move move ON move.payment_id = payment.id
                                 WHERE payment.is_matched IS NOT TRUE
                                   AND payment.payment_type = %s
                                   AND move.state = 'posted'
                                   AND move.journal_id = ANY(%s)
                              GROUP BY move.company_id, move.journal_id, move.currency_id
                            """, [move_type, self.env['account.journal'].search(
                        [('default_account_id', '=', account_id.id)]).ids])  # We must obtain all outstanding balances for the account
                    query_result = self.env.cr.fetchall()
                    amount_result = sum(sum(j for j in t)
                                        for t in query_result)
                    if move_type == 'outbound':
                        account_outbound = -amount_result
                    if move_type == 'inbound':
                        account_inbound = amount_result

                show_account_detail_mode = False

                subformula = ''
                subformula = expression_id.subformula

                if subformula == '-sum':
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
            report_lines=account_financial_report_er_l10n_py.line_ids.filtered(
                lambda x: not x.parent_id),
            padding=1,
            headers=True,
            quantity_headers=False,
            hide_empty_lines=True,
            force_print_from_report_totals=True,
            force_report_totals=account_financial_report_er_l10n_py_report_informations,
            account_report_id=account_financial_report_er_l10n_py,
        )

        pdf = CustomPDF()
        pdf.set_font("Arial", "", 6)
        pdf.start_page_number = self.registration_id.current_number
        pdf.company = self.company_id
        if self.registration_id.signature_image:
            pdf.signature_image = base64.b64decode(
                self.registration_id.signature_image)
        if self.company_id.show_inventory_book_base_report_bs_details:
            col_widths = (10, 50, 10, 10, 10)
            col_number_format = (0, 2, 3, 4)
        else:
            col_widths = (50, 10, 10)
            col_number_format = (1, 2)

        if debug_mode:
            col_widths += (10,)
        for TABLE_DATA in [TABLE_DATA_BS, TABLE_DATA_IS]:
            if TABLE_DATA == TABLE_DATA_BS:
                pdf.title = "Libro Inventario - Balance General"
            if TABLE_DATA == TABLE_DATA_IS:
                pdf.title = "Libro Inventario - Estado de Resultados"
            pdf.add_page()
            with pdf.table(col_widths=col_widths) as table:
                for line_count, data_row in enumerate(TABLE_DATA):
                    row = table.row()
                    for column_count, data in enumerate(data_row):
                        if column_count in col_number_format and line_count > 0:
                            row.cell(text=format_number_to_string(
                                data), align='R')
                        else:
                            row.cell(text=remove_unwanted_characters(
                                str(data)), align='L')

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
        self.cell(-20, 2, f"Nro: {self.start_page_number +
                  self.page_no()}", align="R", ln=True)
        self.cell(0, 5, self.company.vat, align="L", ln=True)
        self.cell(
            0, 5, self.company.street if self.company.street else '', align="L", ln=True)
        self.set_font("Arial", "B", 14)
        self.cell(0, 20, self.title, align="C", ln=True)
        if self.subtitle:
            self.cell(0, 10, self.subtitle, align="C", ln=True)
