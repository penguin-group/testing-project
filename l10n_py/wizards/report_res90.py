from odoo import api, fields, models, exceptions

import calendar
import datetime
import os
import random
from zipfile import ZipFile


class ReportRes90(models.TransientModel):
    _name = 'report.res90'
    _description = 'Res 90 Wizard'

    obligation_type = fields.Selection(string="Tipo de obligación", selection=[(
        'mensual', '955 - Registro mensual de comprobantes'), ('anual', '956 - Registro anual de comprobantes')], default='mensual', required=True)
    month = fields.Integer(string='Mes', default=0)
    year = fields.Integer(string='Año', default=0, required=True)
    version = fields.Integer(string="Versión", default=1, required=True)

    @api.constrains('month', 'year', 'version', 'obligation_type')
    def check_values(self):
        if self.obligation_type == 'mensual' and (self.month < 1 or self.month > 12):
            raise exceptions.ValidationError('Mes incorrecto')
        if self.year < 2021:
            raise exceptions.ValidationError('Año incorrecto')
        if self.version < 1 or self.version > 9999:
            raise exceptions.ValidationError('Versión incorrecta')

        return

    def button_generate_file(self):
        facturas_ventas = self.get__invoices(self.year, self.month, 'ventas')
        facturas_compras = self.get__invoices(self.year, self.month, 'compras')
        valores_ventas = self.get_sales_values(facturas_ventas)
        valores_compras = self.get_purchase_values(facturas_compras)
        return self.generate_file(self.year, valores_ventas, valores_compras, self.version, month=self.month)

    @api.model
    def get__invoices(self, year, month, tipo):

        fecha_inicio = datetime.date(year, month, 1)
        ultimo_dia = calendar.monthrange(year, month)[1]
        fecha_fin = datetime.date(year, month, ultimo_dia)
        if tipo == 'ventas':
            ventas_invoice_ids = self.env['account.move'].search(
                [('move_type', 'in', ['out_invoice', 'in_refund']), ('journal_id.exclude_res90', '=', False), ('exclude_res90', '=', False), (
                    'invoice_date', '>=', fecha_inicio), ('invoice_date', '<=', fecha_fin), ('state', '=', 'posted'), ('company_id', '=', self.env.company.id)])
            return ventas_invoice_ids.sorted(lambda x: x.name)
        elif tipo == 'compras':
            compras_invoice_ids = self.env['account.move'].search(
                [('move_type', 'in', ['in_invoice', 'out_refund']), ('journal_id.exclude_res90', '=', False), ('exclude_res90', '=', False), (
                    'invoice_date', '>=', fecha_inicio), ('invoice_date', '<=', fecha_fin), ('state', '=', 'posted'), ('company_id', '=', self.env.company.id)])
            return compras_invoice_ids.sorted(key=lambda x: x.date)

    @api.model
    def get_sales_values(self, facturas):
        valores = []

        for i in facturas:
            reg = {
                'o1': 1,
                'o2': i.get_id_type(),
                'o3': i.get_identification(),
                'o4': i.get_name_partner(),
                'o5': i.get_receipt_type(),
                'o6': i.get_receipt_date(),
                'o7': i.get_stamped(),
                'o8': i.get_receipt_number(),
                'o9': i.get_amount10(),
                'o10': i.get_amount5(),
                'o11': i.get_exempt_amount(),
                'o12': i.get_total_amount(),
                'o13': i.get_sale_condition(),
                'o14': i.get_foreign_currency_operation(),
                'o15': i.get_imput_vat(),
                'o16': i.get_imput_ire(),
                'o17': i.get_impute_irp_rsp(),
                'o18': i.get_associated_voucher_number(),
                'o19': i.get_associated_receipt_stamping()
            }
            valores.append(reg)
        valores_archivo = ''
        for val in valores:
            valores_archivo = valores_archivo + "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                val.get('o1'), val.get('o2'), val.get('o3'), val.get('o4'), val.get('o5'), val.get('o6'), val.get(
                    'o7'), val.get('o8'), val.get('o9'), val.get('o10'), val.get('o11'), val.get('o12'), val.get('o13'), val.get('o14'), val.get('o15'),
                val.get('o16'), val.get('o17'), val.get('o18'), val.get('o19'))

        return valores_archivo

    @api.model
    def get_purchase_values(self, facturas):
        valores = []

        for i in facturas:
            reg = {
                'o1': 2,
                'o2': i.get_id_type(),
                'o3': i.get_identification(),
                'o4': i.get_name_partner(),
                'o5': i.get_receipt_type(),
                'o6': i.get_receipt_date(),
                'o7': i.get_stamped(),
                'o8': i.get_receipt_number(),
                'o9': i.get_amount10(),
                'o10': i.get_amount5(),
                'o11': i.get_exempt_amount(),
                'o12': i.get_total_amount(),
                'o13': i.get_sale_condition(),
                'o14': i.get_foreign_currency_operation(),
                'o15': i.get_imput_vat(),
                'o16': i.get_imput_ire(),
                'o17': i.get_impute_irp_rsp(),
                'o18': i.get_no_impute(),
                'o19': i.get_associated_voucher_number(),
                'o20': i.get_associated_receipt_stamping()
            }
            valores.append(reg)
        valores_archivo = ''
        for val in valores:
            valores_archivo = valores_archivo + "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
                val.get('o1'), val.get('o2'), val.get('o3'), val.get('o4'), val.get('o5'), val.get('o6'), val.get(
                    'o7'), val.get('o8'), val.get('o9'), val.get('o10'), val.get('o11'), val.get('o12'), val.get('o13'), val.get('o14'), val.get('o15'),
                val.get('o16'), val.get('o17'), val.get('o18'), val.get('o19'), val.get('o20'))

        return valores_archivo



    def generate_file(self, year, valores_ventas, valores_compras, version, month=False):
        ruc_empresa = self.env.company.vat
        if ruc_empresa:
            ruc_empresa = ruc_empresa.split('-')[0]

        if self.obligation_type == 'mensual':
            # ZIP
            os.chdir('/tmp')
            nombre_archivo_zip = "%s_REG_%s%s_Z%s.zip" % (
                ruc_empresa, str(self.month).zfill(2), self.year, str(self.version).zfill(4))
            nombre_archivo_unico = nombre_archivo_zip + str(datetime.datetime.today())
            zipObj = ZipFile(nombre_archivo_unico, 'w')
            limite_lineas = 999

            # VENTAS

            tandas_valores_ventas = valores_ventas.split('\n')
            tandas_valores_ventas = [tandas_valores_ventas[i:i + limite_lineas] for i in range(0, len(tandas_valores_ventas), limite_lineas)]
            for c, tanda_valores in enumerate(tandas_valores_ventas):
                tanda_valores_a_escribir = '\n'.join(tanda_valores)
                nombre_archivo = "%s_REG_%s%s_V%s" % (
                    ruc_empresa,
                    str(self.month).zfill(2),
                    self.year,
                    str(c + self.version).rjust(4, '0')
                )
                nombre_archivo += '.txt'
                archivo = open(nombre_archivo, 'w')
                archivo.write(tanda_valores_a_escribir)
                archivo.close()
                zipObj.write(nombre_archivo)

            # COMPRAS

            tandas_valores_compras = valores_compras.split('\n')
            tandas_valores_compras = [tandas_valores_compras[i:i + limite_lineas] for i in range(0, len(tandas_valores_compras), limite_lineas)]
            for c, tanda_valores in enumerate(tandas_valores_compras):
                tanda_valores_a_escribir = '\n'.join(tanda_valores)
                nombre_archivo = "%s_REG_%s%s_C%s" % (
                    ruc_empresa,
                    str(self.month).zfill(2),
                    self.year,
                    str(c + self.version).rjust(4, '0')
                )
                nombre_archivo += '.txt'
                archivo = open(nombre_archivo, 'w')
                archivo.write(tanda_valores_a_escribir)
                archivo.close()
                zipObj.write(nombre_archivo)

            zipObj.close()
            return {
                'type': 'ir.actions.act_url',
                'url': '/res90/download_file?file=%s&filename=%s' % (nombre_archivo_unico, nombre_archivo_zip),
                'target': 'new',
            }
