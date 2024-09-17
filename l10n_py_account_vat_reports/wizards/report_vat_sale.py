from odoo import models, fields, api, release
import xlsxwriter
import base64


class ReportVatSaleWizard(models.TransientModel):
    _name = 'report.vat.sale.wizard'

    date_start = fields.Date(string='Desde', required=True)
    date_end = fields.Date(string='Hasta', required=True)

    def print_report(self):
        datas = {
            'date_start': self.date_start,
            'date_end': self.date_end,
        }

        return self.env.ref('l10n_py_account_vat_reports.report_vat_sale_report').report_action(self, data=datas)


class ReportVatSale(models.AbstractModel):
    _name = 'report.l10n_py_account_vat_reports.report_vat_sale'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, datas):

        invoices = self.env['account.move'].search(
            [('move_type', '=', 'out_invoice'), ('state', 'in', ['posted', 'cancel']),
             ('invoice_date', '>=', datas.date_start),
             ('invoice_date', '<=', datas.date_end)])
        global sheet
        global f_bold
        global f_number
        global position_x
        global position_y
        sheet = workbook.add_worksheet('Hoja 1')
        f_bold = workbook.add_format({'bold': True})
        f_number = workbook.add_format({'num_format': True, 'align': 'right'})
        f_number.set_num_format('#,##0')
        f_number_total = workbook.add_format(
            {'num_format': True, 'align': 'right', 'bold': True})
        f_number_total.set_num_format('#,##0')
        f_wrapped_text_bold = workbook.add_format({'bold': True})
        f_wrapped_text_bold.set_text_wrap()

        position_x = 0
        position_y = 0

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

        simpleWrite("Razon social:", f_bold)
        rightAndWrite(self.env.company.name)
        breakAndWrite("RUC:", f_bold)
        rightAndWrite(self.env.company.partner_id.vat)
        breakAndWrite("Periodo:", f_bold)
        rightAndWrite("Del " + datas.date_start.strftime("%d/%m/%Y") +
                      " al " + datas.date_end.strftime('%d/%m/%Y'))
        addBreak()
        addRight()
        addRight()
        addRight()
        addRight()
        simpleWrite('Libro de ventas - Ley 125/91', f_bold)
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
            cnt += 1
            if i.state != 'cancel':
                amount_total_invoice = i.amount_total
            else:
                amount_total_invoice = 0

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

            if i.currency_id != self.env.company.currency_id:
                balance = 1
                amount_currency = 1
                balance = abs(i.line_ids.filtered(
                    lambda x: x.currency_id == i.currency_id and x.account_id.account_type in ['asset_receivable', 'liability_payable'])[0].balance)
                amount_currency = abs(
                    i.line_ids.filtered(
                        lambda x: x.currency_id == i.currency_id and x.account_id.account_type in ['asset_receivable', 'liability_payable'])[
                        0].amount_currency)
                if balance > 0 and amount_currency > 0:
                    currency_rate = balance / amount_currency
                else:
                    currency_rate = 1

                amount_total_invoice = i.amount_total_signed
                base10 = base10 * currency_rate
                vat10 = vat10 * currency_rate
                base5 = base5 * currency_rate
                vat5 = vat5 * currency_rate
                exempt = exempt * currency_rate

            amount_total_all += amount_total_invoice
            amount_total_base10 += base10
            amount_total_base5 += base5
            amount_total_vat10 += vat10
            amount_total_vat5 += vat5
            amount_total_exempt += exempt

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
                rightAndWrite(base10, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(vat10, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(base5, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(vat5, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(exempt, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(amount_total_invoice, f_number)
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
             ('invoice_date', '>=', datas.date_start),
             ('invoice_date', '<=', datas.date_end)])

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
            if i.state != 'cancel':
                amount_total_invoice = i.amount_total
            else:
                amount_total_invoice = 0
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

            if i.currency_id != self.env.company.currency_id:
                balance = 1
                amount_currency = 1
                balance = abs(i.line_ids.filtered(
                    lambda x: x.currency_id == i.currency_id and x.account_id.account_type in ['asset_receivable', 'liability_payable'])[0].balance)
                amount_currency = abs(
                    i.line_ids.filtered(
                        lambda x: x.currency_id == i.currency_id and x.account_id.account_type in ['asset_receivable', 'liability_payable'])[
                        0].amount_currency)
                if balance > 0 and amount_currency > 0:
                    currency_rate = balance / amount_currency
                else:
                    currency_rate = 1
                amount_total_invoice = i.amount_total_signed
                base10 = base10 * currency_rate
                vat10 = vat10 * currency_rate
                base5 = base5 * currency_rate
                vat5 = vat5 * currency_rate
                exempt = exempt * currency_rate

            amount_total_all += amount_total_invoice
            amount_total_base10 += base10
            amount_total_base5 += base5
            amount_total_vat10 += vat10
            amount_total_vat5 += vat5
            amount_total_exempt += exempt

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
                rightAndWrite(base10, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(vat10, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(base5, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(vat5, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(exempt, f_number)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(amount_total_invoice, f_number)
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
