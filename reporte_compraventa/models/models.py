# -*- coding: utf-8 -*-

from odoo import models, fields, api, release
import xlsxwriter
import base64


class WizardReporteCompra(models.TransientModel):
    _name = 'reporte_compraventa.wizardcompra'

    fecha_inicio = fields.Date(string='Fecha Inicio', required=True)
    fecha_fin = fields.Date(string='Fecha Fin', required=True)

    def print_report(self):
        datas = {
            'fecha_inicio': self.fecha_inicio,
            'fecha_fin': self.fecha_fin,

        }

        return self.env.ref('reporte_compraventa.account_invoices_compras_action').report_action(self, data=datas)

    def print_report_xlsx(self):
        return self.env.ref('reporte_compraventa.reporte_compra_xlsx_action').report_action(self)


class ReporteComprasXLSX(models.AbstractModel):
    _name = 'report.reporte_compraventa.reporte_compra_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def get_facturas_libro_compra(self, fecha_inicio, fecha_fin):
        return self.env['account.move'].search([
            ('move_type', '=', 'in_invoice'),
            ('state', 'in', ['posted']),
            ('invoice_date', '>=', fecha_inicio),
            ('invoice_date', '<=', fecha_fin),
            ('line_ids.tax_ids', '!=', False),
        ])

    def get_exenta_5_10(self, invoice_line):
        pyg = self.env.ref('base.PYG')
        
        def get_line_amount(line):
            if line.currency_id.id == pyg.id:
                amount = line.price_total
            else:
                if line.move_id.freeze_currency_rate:
                    amount = line.price_total * line.tipo_cambio
                else:
                    amount = line.currency_id._convert(line.price_total, pyg, line.company_id, line.date)
            return amount
        
        base10 = 0
        iva10 = 0
        base5 = 0
        iva5 = 0
        exentas = 0
        imponible_importaciones = 0
        if invoice_line.tax_ids and invoice_line.tax_ids[0].amount == 10:
            base10 += get_line_amount(invoice_line) / 1.1
            iva10 += get_line_amount(invoice_line) / 11
        if invoice_line.tax_ids and invoice_line.tax_ids[0].amount == 5:
            base5 += get_line_amount(invoice_line) / 1.05
            iva5 += get_line_amount(invoice_line) / 21
        if (invoice_line.tax_ids and invoice_line.tax_ids[0].amount == 0) or not invoice_line.tax_ids:
            exentas += get_line_amount(invoice_line)
        return base10, iva10, base5, iva5, exentas, imponible_importaciones

    def get_proveedor(self, invoice, campo):
        if campo == 'name':
            return invoice.partner_id.name
        if campo == 'vat':
            return invoice.partner_id.vat

    def generate_xlsx_report(self, workbook, data, datas):

        facturas = self.get_facturas_libro_compra(datas.fecha_inicio, datas.fecha_fin)
        global sheet
        global bold
        global num_format
        global position_x
        global position_y
        sheet = workbook.add_worksheet('Hoja 1')
        bold = workbook.add_format({'bold': True})
        numerico = workbook.add_format({'num_format': True, 'align': 'right'})
        numerico.set_num_format('#,##0')
        numerico_total = workbook.add_format(
            {'num_format': True, 'align': 'right', 'bold': True})
        numerico_total.set_num_format('#,##0')
        wrapped_text = workbook.add_format()
        wrapped_text.set_text_wrap()
        wrapped_text_bold = workbook.add_format({'bold': True})
        wrapped_text_bold.set_text_wrap()

        position_x = 0
        position_y = 0

        def addSalto():
            global position_x
            global position_y
            position_x = 0
            position_y += 1

        def addRight():
            global position_x
            position_x += 1

        def breakAndWrite(to_write, format=None):
            global sheet
            addSalto()
            sheet.write(position_y, position_x, to_write, format)

        def simpleWrite(to_write, format=None):
            global sheet
            sheet.write(position_y, position_x, to_write, format)

        def rightAndWrite(to_write, format=None):
            global sheet
            addRight()
            sheet.write(position_y, position_x, to_write, format)

        simpleWrite("Razon social:", bold)
        rightAndWrite(self.env.company.name)
        breakAndWrite("RUC:", bold)
        rightAndWrite(self.env.company.partner_id.vat)
        breakAndWrite("Periodo:", bold)
        rightAndWrite("Del " + datas.fecha_inicio.strftime("%d/%m/%Y") +
                      " al " + datas.fecha_fin.strftime('%d/%m/%Y'))
        addSalto()
        addRight()
        addRight()
        addRight()
        addRight()
        simpleWrite('Libro de compras - Ley 125/91', bold)
        breakAndWrite("Nro", bold)
        rightAndWrite("Fecha", bold)
        rightAndWrite("Proveedor", bold)
        rightAndWrite("RUC del Proveedor", wrapped_text_bold)
        rightAndWrite("Tipo doc.", bold)
        rightAndWrite("Nro. doc.", bold)
        rightAndWrite("Timbrado", bold)
        rightAndWrite("Importe sin IVA 10%", wrapped_text_bold)
        rightAndWrite("Debito fiscal 10%", wrapped_text_bold)
        rightAndWrite("Importe sin IVA 5%", wrapped_text_bold)
        rightAndWrite("Debito fiscal 5%", wrapped_text_bold)
        rightAndWrite("Importes exentos", wrapped_text_bold)
        rightAndWrite("Total", wrapped_text_bold)
        rightAndWrite("Base Imponible Importaciones", wrapped_text_bold)

        cont = 0
        total_gral_base10 = 0
        total_gral_iva10 = 0
        total_gral_base5 = 0
        total_gral_iva5 = 0
        total_gral_exentas = 0
        total_gral_total = 0
        total_imponible_importaciones = 0
        for i in facturas.sorted(key=lambda r: r.invoice_date):
            cont += 1

            base10 = 0
            iva10 = 0
            base5 = 0
            iva5 = 0
            exentas = 0
            imponible_importaciones = 0
            for t in i.filtered(lambda x: x.state != 'cancel').invoice_line_ids:
                values = self.get_exenta_5_10(t)
                base10 += values[0]
                iva10 += values[1]
                base5 += values[2]
                iva5 += values[3]
                exentas += values[4]
                imponible_importaciones += values[5]

            total_factura = base10 + iva10 + base5 + iva5 + exentas

            total_gral_base10 += base10
            total_gral_iva10 += iva10
            total_gral_base5 += base5
            total_gral_iva5 += iva5
            total_gral_exentas += exentas
            total_gral_total += total_factura
            total_imponible_importaciones += imponible_importaciones

            breakAndWrite(cont)
            rightAndWrite(i.invoice_date.strftime("%d/%m/%Y"))
            # rightAndWrite(i.partner_id.name)
            rightAndWrite(self.get_proveedor(i, 'name'))
            # rightAndWrite(i.partner_id.vat)
            rightAndWrite(self.get_proveedor(i, 'vat'))

            if i.invoice_date < i.invoice_date_due:
                rightAndWrite("Credito")
            else:
                rightAndWrite("Contado")
            rightAndWrite(i.ref)
            rightAndWrite(i.timbrado_proveedor or '')
            rightAndWrite(base10, numerico)
            rightAndWrite(iva10, numerico)
            rightAndWrite(base5, numerico)
            rightAndWrite(iva5, numerico)
            rightAndWrite(exentas, numerico)
            rightAndWrite(total_factura, numerico)
            rightAndWrite(imponible_importaciones, numerico)

        addSalto()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        rightAndWrite(total_gral_base10, numerico_total)
        rightAndWrite(total_gral_iva10, numerico_total)
        rightAndWrite(total_gral_base5, numerico_total)
        rightAndWrite(total_gral_iva5, numerico_total)
        rightAndWrite(total_gral_exentas, numerico_total)
        rightAndWrite(total_gral_total, numerico_total)
        rightAndWrite(total_imponible_importaciones, numerico_total)

        notas = self.env['account.move'].search(
            [('move_type', '=', 'out_refund'), ('state', 'in', ['posted', 'cancel']),
             ('invoice_date', '>=', datas.fecha_inicio),
             ('invoice_date', '<=', datas.fecha_fin), ('line_ids.tax_ids', '!=', False)])

        breakAndWrite('Notas de crédito emitidas', bold)
        breakAndWrite("Nro", bold)
        rightAndWrite("Fecha", bold)
        rightAndWrite("Cliente", bold)
        rightAndWrite("RUC o CI del Cliente", wrapped_text_bold)
        rightAndWrite("Tipo doc.", bold)
        rightAndWrite("Nro. doc.", bold)
        rightAndWrite("Importe sin IVA 10%", wrapped_text_bold)
        rightAndWrite("Debito fiscal 10%", wrapped_text_bold)
        rightAndWrite("Importe sin IVA 5%", wrapped_text_bold)
        rightAndWrite("Debito fiscal 5%", wrapped_text_bold)
        rightAndWrite("Importes exentos", wrapped_text_bold)
        rightAndWrite("Importe total con IVA incluido", wrapped_text_bold)

        cont = 0
        total_gral_total = 0
        total_gral_base10 = 0
        total_gral_base5 = 0
        total_gral_iva10 = 0
        total_gral_iva5 = 0
        total_gral_exentas = 0
        for i in notas.sorted(key=lambda x: x.name):
            cont += 1
            base10 = 0
            base5 = 0
            exentas = 0
            iva10 = 0
            iva5 = 0
            for t in i.filtered(lambda x: x.state != 'cancel').invoice_line_ids:
                values = self.get_exenta_5_10(t)
                base10 += values[0]
                iva10 += values[1]
                base5 += values[2]
                iva5 += values[3]
                exentas += values[4]

            total_factura = base10 + iva10 + base5 + iva5 + exentas

            total_gral_total += total_factura
            total_gral_base10 += base10
            total_gral_base5 += base5
            total_gral_iva10 += iva10
            total_gral_iva5 += iva5
            total_gral_exentas += exentas

            breakAndWrite(cont)
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
                rightAndWrite(base10, numerico)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(iva10, numerico)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(base5, numerico)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(iva5, numerico)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(exentas, numerico)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(total_factura, numerico)
            else:
                rightAndWrite(0)
        addSalto()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        rightAndWrite(total_gral_base10, numerico_total)
        rightAndWrite(total_gral_iva10, numerico_total)
        rightAndWrite(total_gral_base5, numerico_total)
        rightAndWrite(total_gral_iva5, numerico_total)
        rightAndWrite(total_gral_exentas, numerico_total)
        rightAndWrite(total_gral_total, numerico_total)


class WizardReporteVenta(models.TransientModel):
    _name = 'reporte_compraventa.wizardventa'

    fecha_inicio = fields.Date(string='Fecha Inicio', required=True)
    fecha_fin = fields.Date(string='Fecha Fin', required=True)

    def print_report(self):
        datas = {
            'fecha_inicio': self.fecha_inicio,
            'fecha_fin': self.fecha_fin,

        }

        return self.env.ref('reporte_compraventa.account_invoices_ventas_action').report_action(self, data=datas)

    def print_report_xlsx(self):
        return self.env.ref('reporte_compraventa.reporte_venta_xlsx_action').report_action(self)


class ReporteVentasXLSX(models.AbstractModel):
    _name = 'report.reporte_compraventa.reporte_venta_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, datas):

        def get_exenta_5_10(invoice_line):
            pyg = self.env.ref('base.PYG')
            
            def get_line_amount(line):
                if line.currency_id.id == pyg.id:
                    amount = line.price_total
                else:
                    if line.move_id.freeze_currency_rate:
                        amount = line.price_total * line.move_id.currency_rate
                    else:
                        amount = line.currency_id._convert(line.price_total, pyg, line.company_id, line.date)
                return amount
            
            base10 = 0
            iva10 = 0
            base5 = 0
            iva5 = 0
            exentas = 0
            imponible_importaciones = 0
            if invoice_line.tax_ids and invoice_line.tax_ids[0].amount == 10:
                base10 += get_line_amount(invoice_line) / 1.1
                iva10 += get_line_amount(invoice_line) / 11
            if invoice_line.tax_ids and invoice_line.tax_ids[0].amount == 5:
                base5 += get_line_amount(invoice_line) / 1.05
                iva5 += get_line_amount(invoice_line) / 21
            if (invoice_line.tax_ids and invoice_line.tax_ids[0].amount == 0) or not invoice_line.tax_ids:
                exentas += get_line_amount(invoice_line)
            return base10, iva10, base5, iva5, exentas, imponible_importaciones

        facturas = self.env['account.move'].search(
            [('move_type', '=', 'out_invoice'), ('state', 'in', ['posted', 'cancel']),
             ('invoice_date', '>=', datas.fecha_inicio),
             ('invoice_date', '<=', datas.fecha_fin)])
        global sheet
        global bold
        global num_format
        global position_x
        global position_y
        sheet = workbook.add_worksheet('Hoja 1')
        bold = workbook.add_format({'bold': True})
        numerico = workbook.add_format({'num_format': True, 'align': 'right'})
        numerico.set_num_format('#,##0')
        numerico_total = workbook.add_format(
            {'num_format': True, 'align': 'right', 'bold': True})
        numerico_total.set_num_format('#,##0')
        wrapped_text = workbook.add_format()
        wrapped_text.set_text_wrap()
        wrapped_text_bold = workbook.add_format({'bold': True})
        wrapped_text_bold.set_text_wrap()

        position_x = 0
        position_y = 0

        def addSalto():
            global position_x
            global position_y
            position_x = 0
            position_y += 1

        def addRight():
            global position_x
            position_x += 1

        def breakAndWrite(to_write, format=None):
            global sheet
            addSalto()
            sheet.write(position_y, position_x, to_write, format)

        def simpleWrite(to_write, format=None):
            global sheet
            sheet.write(position_y, position_x, to_write, format)

        def rightAndWrite(to_write, format=None):
            global sheet
            addRight()
            sheet.write(position_y, position_x, to_write, format)

        simpleWrite("Razon social:", bold)
        rightAndWrite(self.env.company.name)
        breakAndWrite("RUC:", bold)
        rightAndWrite(self.env.company.partner_id.vat)
        breakAndWrite("Periodo:", bold)
        rightAndWrite("Del " + datas.fecha_inicio.strftime("%d/%m/%Y") +
                      " al " + datas.fecha_fin.strftime('%d/%m/%Y'))
        addSalto()
        addRight()
        addRight()
        addRight()
        addRight()
        simpleWrite('Libro de ventas - Ley 125/91', bold)
        breakAndWrite("Nro", bold)
        rightAndWrite("Fecha", bold)
        rightAndWrite("Cliente", bold)
        rightAndWrite("RUC o CI del Cliente", wrapped_text_bold)
        rightAndWrite("Tipo doc.", bold)
        rightAndWrite("Nro. doc.", bold)
        rightAndWrite("Importe sin IVA 10%", wrapped_text_bold)
        rightAndWrite("Debito fiscal 10%", wrapped_text_bold)
        rightAndWrite("Importe sin IVA 5%", wrapped_text_bold)
        rightAndWrite("Debito fiscal 5%", wrapped_text_bold)
        rightAndWrite("Importes exentos", wrapped_text_bold)
        rightAndWrite("Importe total facturado con IVA incluido", wrapped_text_bold)

        cont = 0
        total_gral_total = 0
        total_gral_base10 = 0
        total_gral_base5 = 0
        total_gral_iva10 = 0
        total_gral_iva5 = 0
        total_gral_exentas = 0
        for i in facturas.sorted(key=lambda x: x.name):
            cont += 1

            base10 = 0
            base5 = 0
            exentas = 0
            iva10 = 0
            iva5 = 0
            imponible_importaciones = 0

            for t in i.filtered(lambda x: x.state != 'cancel').invoice_line_ids:
                values = get_exenta_5_10(t)
                base10 += values[0]
                iva10 += values[1]
                base5 += values[2]
                iva5 += values[3]
                exentas += values[4]
                imponible_importaciones += values[5]

            total_factura = base10 + iva10 + base5 + iva5 + exentas

            total_gral_total += total_factura
            total_gral_base10 += base10
            total_gral_base5 += base5
            total_gral_iva10 += iva10
            total_gral_iva5 += iva5
            total_gral_exentas += exentas

            breakAndWrite(cont)
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
                    rightAndWrite("Credito")
                else:
                    rightAndWrite("Contado")
            else:
                rightAndWrite("")
            rightAndWrite(i.name)

            if i.state != 'cancel':
                rightAndWrite(base10, numerico)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(iva10, numerico)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(base5, numerico)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(iva5, numerico)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(exentas, numerico)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(total_factura, numerico)
            else:
                rightAndWrite(0)

        addSalto()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        rightAndWrite(total_gral_base10, numerico_total)
        rightAndWrite(total_gral_iva10, numerico_total)
        rightAndWrite(total_gral_base5, numerico_total)
        rightAndWrite(total_gral_iva5, numerico_total)
        rightAndWrite(total_gral_exentas, numerico_total)
        rightAndWrite(total_gral_total, numerico_total)

        notas = self.env['account.move'].search(
            [('move_type', '=', 'in_refund'), ('state', 'in', ['posted']),
             ('invoice_date', '>=', datas.fecha_inicio),
             ('invoice_date', '<=', datas.fecha_fin)])

        breakAndWrite('Notas de crédito recibidas', bold)
        breakAndWrite("Nro", bold)
        rightAndWrite("Fecha", bold)
        rightAndWrite("Proveedor", bold)
        rightAndWrite("RUC o CI del Proveedor", wrapped_text_bold)
        rightAndWrite("Tipo doc.", bold)
        rightAndWrite("Nro. doc.", bold)
        rightAndWrite("Importe sin IVA 10%", wrapped_text_bold)
        rightAndWrite("Debito fiscal 10%", wrapped_text_bold)
        rightAndWrite("Importe sin IVA 5%", wrapped_text_bold)
        rightAndWrite("Debito fiscal 5%", wrapped_text_bold)
        rightAndWrite("Importes exentos", wrapped_text_bold)
        rightAndWrite("Importe total con IVA incluido", wrapped_text_bold)

        cont = 0
        total_gral_total = 0
        total_gral_base10 = 0
        total_gral_base5 = 0
        total_gral_iva10 = 0
        total_gral_iva5 = 0
        total_gral_exentas = 0
        for i in notas.sorted(key=lambda x: x.invoice_date):
            cont += 1

            base10 = 0
            iva10 = 0
            base5 = 0
            iva5 = 0
            exentas = 0
            imponible_importaciones = 0
            for t in i.filtered(lambda x: x.state != 'cancel').invoice_line_ids:
                values = self.get_exenta_5_10(t)
                base10 += values[0]
                iva10 += values[1]
                base5 += values[2]
                iva5 += values[3]
                exentas += values[4]
                imponible_importaciones += values[5]

            total_factura = base10 + iva10 + base5 + iva5 + exentas

            total_gral_base10 += base10
            total_gral_iva10 += iva10
            total_gral_base5 += base5
            total_gral_iva5 += iva5
            total_gral_exentas += exentas
            total_gral_total += total_factura

            breakAndWrite(cont)
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
                rightAndWrite(base10, numerico)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(iva10, numerico)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(base5, numerico)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(iva5, numerico)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(exentas, numerico)
            else:
                rightAndWrite(0)
            if i.state != 'cancel':
                rightAndWrite(total_factura, numerico)
            else:
                rightAndWrite(0)

        addSalto()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        rightAndWrite(total_gral_base10, numerico_total)
        rightAndWrite(total_gral_iva10, numerico_total)
        rightAndWrite(total_gral_base5, numerico_total)
        rightAndWrite(total_gral_iva5, numerico_total)
        rightAndWrite(total_gral_exentas, numerico_total)
        rightAndWrite(total_gral_total, numerico_total)
