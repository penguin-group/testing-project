from odoo import models, fields, api, release, _
from odoo.exceptions import ValidationError
import xlsxwriter
import base64
import tempfile


class ReportVatSaleWizard(models.TransientModel):
    _name = 'report.vat.sale.wizard'
    _description = "VAT Sale Report Wizard"

    date_start = fields.Date(string='From', required=True)
    date_end = fields.Date(string='To', required=True)
    excel_file = fields.Binary("Excel File", readonly=True)


    def print_report(self):
        if self.env.company.partner_id.country_id.code == 'PY':
            return self.generate_xlsx_report()
        else:
            raise ValidationError(_("This report is only for Paraguay-based companies."))

    def generate_xlsx_report(self):
        self.ensure_one()

        filename = 'vat_sale.xlsx'
        fullpath = tempfile.gettempdir() + '/' + filename
        workbook = xlsxwriter.Workbook(fullpath)

        invoices = self.env['account.move'].search(
            [('move_type', '=', 'out_invoice'), 
            ('state', 'in', ['posted', 'cancel']),
            ('invoice_date', '>=', self.date_start),
            ('invoice_date', '<=', self.date_end),
            ('company_id', '=', self.env.company.id)])
        global sheet
        global f_bold
        global f_number
        global position_x
        global position_y
        sheet = workbook.add_worksheet('Hoja 1')

        # Width of the columns
        sheet.set_column('A:A', 4)
        sheet.set_column('B:B', 11)
        sheet.set_column('C:C', 25)
        sheet.set_column('D:E', 10)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:L', 10)

        # Formats
        f_bold = workbook.add_format({'bold': True})
        f_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter'        
        })
        f_number = workbook.add_format({'num_format': True, 'align': 'right'})
        f_number.set_num_format('#,##0')
        f_number_total = workbook.add_format(
            {'num_format': True, 'align': 'right', 'bold': True})
        f_number_total.set_num_format('#,##0')
        f_wrapped_text_bold = workbook.add_format({'bold': True})
        f_wrapped_text_bold.set_text_wrap()

        def addBreak():
            global position_x
            global position_y
            position_x = 0
            position_y += 1

        def addRight():
            global position_x
            position_x += 1

        def breakAndWrite(to_write, format=None):
            global sheet
            addBreak()
            sheet.write(position_y, position_x, to_write, format)

        def simpleWrite(to_write, format=None):
            global sheet
            sheet.write(position_y, position_x, to_write, format)

        def rightAndWrite(to_write, format=None):
            global sheet
            addRight()
            sheet.write(position_y, position_x, to_write, format)

        sheet.merge_range('A1:B1', 'Razón Social', f_bold)
        sheet.merge_range('C1:D1', self.env.company.name)
        sheet.merge_range('A2:B2', 'RUC', f_bold)
        sheet.merge_range('C2:D2', self.env.company.partner_id.vat)
        sheet.merge_range('A3:B3', 'Periodo', f_bold)
        sheet.merge_range('C3:D3', 
            "De " + self.date_start.strftime("%d/%m/%Y") + " a " + self.date_end.strftime('%d/%m/%Y'))
        sheet.merge_range('A4:L4', 'Libro de ventas - Ley 125/91', f_title)        

        position_x = 0
        position_y = 3
        
        breakAndWrite("Nro", f_bold)
        rightAndWrite("Fecha", f_bold)
        rightAndWrite("Cliente", f_bold)
        rightAndWrite("RUC o CI del Cliente", f_wrapped_text_bold)
        rightAndWrite("Tipo doc.", f_bold)
        rightAndWrite("Nro. doc.", f_bold)
        rightAndWrite("Importe sin IVA 10%", f_wrapped_text_bold)
        rightAndWrite("Debito fiscal 10%", f_wrapped_text_bold)
        rightAndWrite("Importe sin IVA 5%", f_wrapped_text_bold)
        rightAndWrite("Debito fiscal 5%", f_wrapped_text_bold)
        rightAndWrite("Importes exentos", f_wrapped_text_bold)
        rightAndWrite("Importe total facturado con IVA incluido", f_wrapped_text_bold)

        cnt = 0
        amount_total_all = 0
        amount_total_base10 = 0
        amount_total_base5 = 0
        amount_total_vat10 = 0
        amount_total_vat5 = 0
        amount_total_exempt = 0
        for i in invoices.sorted(key=lambda x: x.name):
            amount_total_base10 += i.amount_base10
            amount_total_vat10 += i.amount_vat10
            amount_total_base5 += i.amount_base5
            amount_total_vat5 += i.amount_vat5
            amount_total_exempt += i.amount_exempt
            amount_total_all += abs(i.amount_total_signed)

            breakAndWrite(cnt)
            if i.state != 'cancel':
                rightAndWrite(i.invoice_date.strftime("%d/%m/%Y"))
            else:
                rightAndWrite("")
            if i.state != 'cancel':
                rightAndWrite(i.partner_id.name)
            else:
                rightAndWrite("Anulado")
            if i.state != 'cancel':
                rightAndWrite(i.partner_id.vat)
            else:
                rightAndWrite("")

            if i.state != 'cancel':
                if i.invoice_date < i.invoice_date_due:
                    rightAndWrite("Crédito")
                else:
                    rightAndWrite("Contado")
            else:
                rightAndWrite("")
            rightAndWrite(i.name)

            if i.state != 'cancel':
                rightAndWrite(i.amount_base10, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(i.amount_vat10, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(i.amount_base5, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(i.amount_vat5, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(i.amount_exempt, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(abs(i.amount_total_signed), f_number)
            else:
                rightAndWrite(0)

        addBreak()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        rightAndWrite(amount_total_base10, f_number_total)
        rightAndWrite(amount_total_vat10, f_number_total)
        rightAndWrite(amount_total_base5, f_number_total)
        rightAndWrite(amount_total_vat5, f_number_total)
        rightAndWrite(amount_total_exempt, f_number_total)
        rightAndWrite(amount_total_all, f_number_total)

        credit_notes = self.env['account.move'].search(
            [('move_type', '=', 'in_refund'), ('state', 'in', ['posted']),
             ('invoice_date', '>=', self.date_start),
             ('invoice_date', '<=', self.date_end)])

        breakAndWrite('Notas de crédito recibidas', f_bold)
        breakAndWrite("Nro", f_bold)
        rightAndWrite("Fecha", f_bold)
        rightAndWrite("Proveedor", f_bold)
        rightAndWrite("RUC o CI del Proveedor", f_wrapped_text_bold)
        rightAndWrite("Tipo doc.", f_bold)
        rightAndWrite("Nro. doc.", f_bold)
        rightAndWrite("Importe sin IVA 10%", f_wrapped_text_bold)
        rightAndWrite("Debito fiscal 10%", f_wrapped_text_bold)
        rightAndWrite("Importe sin IVA 5%", f_wrapped_text_bold)
        rightAndWrite("Debito fiscal 5%", f_wrapped_text_bold)
        rightAndWrite("Importes exentos", f_wrapped_text_bold)
        rightAndWrite("Importe total con IVA incluido", f_wrapped_text_bold)

        cnt = 0
        amount_total_all = 0
        amount_total_base10 = 0
        amount_total_base5 = 0
        amount_total_vat10 = 0
        amount_total_vat5 = 0
        amount_total_exempt = 0
        for i in credit_notes.sorted(key=lambda x: x.invoice_date):
            cnt += 1
            amount_total_all += abs(i.amount_total_signed)
            amount_total_base10 += i.amount_base10
            amount_total_base5 += i.amount_base5
            amount_total_vat10 += i.amount_vat10
            amount_total_vat5 += i.amount_vat5 
            amount_total_exempt += i.amount_exempt

            breakAndWrite(cnt)
            if i.state != 'cancel':
                rightAndWrite(i.invoice_date.strftime("%d/%m/%Y"))
            else:
                rightAndWrite("")
            if i.state != 'cancel':
                rightAndWrite(i.partner_id.name)
            else:
                rightAndWrite("Anulado")
            if i.state != 'cancel':
                rightAndWrite(i.partner_id.vat)
            else:
                rightAndWrite("")

            if i.state != 'cancel':

                rightAndWrite("Nota de crédito")
            else:
                rightAndWrite("")
            rightAndWrite(i.ref)

            if i.state != 'cancel':
                rightAndWrite(i.amount_base10, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(i.amount_vat10, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(i.amount_base5, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(i.amount_vat5, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(i.amount_exempt, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(abs(i.amount_total_signed), f_number)
            else:
                rightAndWrite(0)

        addBreak()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        rightAndWrite(amount_total_base10, f_number_total)
        rightAndWrite(amount_total_vat10, f_number_total)
        rightAndWrite(amount_total_base5, f_number_total)
        rightAndWrite(amount_total_vat5, f_number_total)
        rightAndWrite(amount_total_exempt, f_number_total)
        rightAndWrite(amount_total_all, f_number_total)

        workbook.close()
        
        with open(fullpath, "rb") as file:
            file_base64 = base64.b64encode(file.read())
        
        self.write({
            'excel_file': file_base64
        })
        
        return {
            'type': 'ir.actions.act_url',
            'name': 'report_vat_sale',
            'url': '/web/content/report.vat.sale.wizard/%s/excel_file/%s?download=true' %
                    (self.id, filename),
        }