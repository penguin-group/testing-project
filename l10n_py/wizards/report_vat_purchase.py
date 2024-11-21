from odoo import models, fields, api, release, _
from odoo.exceptions import ValidationError
import xlsxwriter
import base64

class ReportVatPurchaseWizard(models.TransientModel):
    _name = 'report.vat.purchase.wizard'
    _description = "VAT Purchase Report Wizard"

    date_start = fields.Date(string='From', required=True)
    date_end = fields.Date(string='To', required=True)

    def print_report(self):        
        if self.env.company.partner_id.country_id.code == 'PY':
            datas = {
                'date_start': self.date_start,
                'date_end': self.date_end,
            }

            return self.env.ref('l10n_py.report_vat_purchase_report').report_action(self, data=datas)
        else:
            raise ValidationError(_("This report is only for Paraguay-based companies."))


class ReportVatPurchase(models.AbstractModel):
    _name = 'report.l10n_py.report_vat_purchase'
    _inherit = 'report.report_xlsx.abstract'
    _description = "VAT Purchase Report"

    def get_purchase_invoices(self, date_start, date_end):
        return self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('state', 'in', ['posted']),
            ('invoice_date', '>=', date_start),
            ('invoice_date', '<=', date_end),
            ('company_id', '=', self.env.company.id),
            ('line_ids.tax_ids', '!=', False),
        ]).filtered(lambda x: not x.foreign_invoice)

    def get_supplier(self, invoice, field_name):
        if invoice.import_clearance:
            partner = self.env['res.partner'].search([('foreign_default_supplier', '=', True)])
            if not partner:
                raise ValidationError(_('A default foreign default supplier must be established in order to continue.'))
        else:
            partner = invoice.partner_id
        if field_name == 'name':
            return partner.name
        if field_name == 'vat':
            return partner.vat

    def generate_xlsx_report(self, workbook, data, datas):
        invoices = self.get_purchase_invoices(datas.date_start, datas.date_end)

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
        sheet.set_column('G:N', 10)

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
            "De " + datas.date_start.strftime("%d/%m/%Y") + " a " + datas.date_end.strftime('%d/%m/%Y'))
        sheet.merge_range('A4:N4', 'Libro de compras - Ley 125/91', f_title)        

        position_x = 0
        position_y = 3

        breakAndWrite("Nro", f_bold)
        rightAndWrite("Fecha", f_bold)
        rightAndWrite("Proveedor", f_bold)
        rightAndWrite("RUC del Proveedor", f_wrapped_text_bold)
        rightAndWrite("Tipo doc.", f_bold)
        rightAndWrite("Nro. doc.", f_bold)
        rightAndWrite("Timbrado", f_bold)
        rightAndWrite("Importe sin IVA 10%", f_wrapped_text_bold)
        rightAndWrite("Debito fiscal 10%", f_wrapped_text_bold)
        rightAndWrite("Importe sin IVA 5%", f_wrapped_text_bold)
        rightAndWrite("Debito fiscal 5%", f_wrapped_text_bold)
        rightAndWrite("Importes exentos", f_wrapped_text_bold)
        rightAndWrite("Total", f_wrapped_text_bold)
        rightAndWrite("Base Imponible Importaciones", f_wrapped_text_bold)

        cnt = 0
        amount_total_base10 = 0
        amount_total_vat10 = 0
        amount_total_base5 = 0
        amount_total_vat5 = 0
        amount_total_exempt = 0
        amount_total_all = 0
        amount_total_imports = 0
        line_total = 0
        
        for i in invoices.sorted(key=lambda r: r.invoice_date):
            cnt += 1
            
            amount_total_base10 += i.amount_base10
            amount_total_base5 += i.amount_base5
            amount_total_vat10 += i.amount_vat10
            amount_total_vat5 += i.amount_vat5 
            amount_total_exempt += i.amount_exempt
            amount_total_imports += i.amount_taxable_imports
            line_total = i.amount_base10 + i.amount_vat10 + i.amount_base5 + i.amount_vat5 + i.amount_exempt
            amount_total_all += line_total

            breakAndWrite(cnt)
            rightAndWrite(i.invoice_date.strftime("%d/%m/%Y"))
            rightAndWrite(self.get_supplier(i, 'name'))
            rightAndWrite(self.get_supplier(i, 'vat'))

            if i.invoice_date < i.invoice_date_due:
                rightAndWrite("Crédito")
            else:
                rightAndWrite("Contado")

            rightAndWrite(i.ref)
            rightAndWrite(i.supplier_invoice_authorization_id.name if i.supplier_invoice_authorization_id else '')
            rightAndWrite(i.amount_base10, f_number)
            rightAndWrite(i.amount_vat10, f_number)
            rightAndWrite(i.amount_base5, f_number)
            rightAndWrite(i.amount_vat5, f_number)
            rightAndWrite(i.amount_exempt, f_number)
            rightAndWrite(line_total, f_number)
            rightAndWrite(i.amount_taxable_imports, f_number)

        addBreak()
        addRight()
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
        rightAndWrite(amount_total_imports, f_number_total)

        credit_notes = self.env['account.move'].search(
            [('move_type', '=', 'out_refund'), ('state', 'in', ['posted', 'cancel']),
             ('invoice_date', '>=', datas.date_start),
             ('invoice_date', '<=', datas.date_end), ('line_ids.tax_ids', '!=', False)])

        breakAndWrite('Notas de crédito emitidas', f_bold)
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
        rightAndWrite("Importe total con IVA incluido", f_wrapped_text_bold)

        cnt = 0
        amount_total_all = 0
        amount_total_base10 = 0
        amount_total_base5 = 0
        amount_total_vat10 = 0
        amount_total_vat5 = 0
        amount_total_exempt = 0
        line_total = 0

        for i in credit_notes.sorted(key=lambda x: x.name):
            cnt += 1
            
            amount_total_base10 += i.amount_base10
            amount_total_base5 += i.amount_base5
            amount_total_vat10 += i.amount_vat10
            amount_total_vat5 += i.amount_vat5 
            amount_total_exempt += i.amount_exempt
            line_total = i.amount_base10 + i.amount_vat10 + i.amount_base5 + i.amount_vat5 + i.amount_exempt
            amount_total_all += line_total

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
                rightAndWrite(line_total, f_number)
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
