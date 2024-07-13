from odoo import _, api, fields, models,exceptions


class WizardCosteo(models.TransientModel):
    _name = 'costeo_importaciones.wizard.costeo'
    _description = 'WizardCosteo'

    purchase_id=fields.Many2one('purchase.order',string="Orden de compra")
    picking_ids=fields.Many2many('stock.picking',compute="compute_picking_ids")
    picking_id=fields.Many2one('stock.picking',string="Recepción")

    @api.depends('purchase_id')
    def compute_picking_ids(self):
        self.picking_ids=self.purchase_id.picking_ids.filtered(lambda x:x.state=='done')

    def button_confirmar(self):
        data={

            'purchase_id':self.purchase_id.id,
            'picking_id':self.picking_id.id,
        }
        return self.env.ref('costeo_importaciones.reporte_costeo_xlsx_action').report_action(self, data=data)
    
class ReporteCosteo(models.AbstractModel):
    _name = 'report.costeo_importaciones.reporte_costeo'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, datas):
        global sheet
        global bold
        global num_format
        global position_x
        global position_y
        sheet = workbook.add_worksheet('Hoja 1')
        bold = workbook.add_format({'bold': True})
        numerico = workbook.add_format({'num_format': True, 'align': 'right'})
        numerico_float = workbook.add_format({'num_format': True, 'align': 'right'})
        numerico.set_num_format('#,##0')
        numerico_float.set_num_format('#,##0.00')
        numerico_total = workbook.add_format(
            {'num_format': True, 'align': 'right', 'bold': True})
        numerico_total_float = workbook.add_format(
            {'num_format': True, 'align': 'right', 'bold': True})
        numerico_total.set_num_format('#,##0')
        numerico_total_float.set_num_format('#,##0.00')
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

            ##########################Inicio de la funcion real###############################
    
        purchase_id=self.env['purchase.order'].browse(data.get('purchase_id'))
        picking_id=self.env['stock.picking'].browse(data.get('picking_id'))
        if not picking_id:
            raise exceptions.ValidationError("Debe seleccionar una recepción hecha para ésta Orden de compra")
        currency_id=self.env.company.currency_id
        sec_currency_id=self.env.company.secondary_currency_id
        
        ###Cabecera del reporte
        
        simpleWrite(self.env.company.name,bold)
        breakAndWrite('Costeo de importación',bold)
        breakAndWrite('Orden de compra:',bold)
        rightAndWrite(purchase_id.name)
        breakAndWrite('Proveedor:',bold)
        rightAndWrite(purchase_id.partner_id.name)
        breakAndWrite('Ref. Proveedor:',bold)
        rightAndWrite(purchase_id.partner_ref if purchase_id.partner_ref else "")
        addRight()
        addRight()
        simpleWrite("Fecha de confirmación:",bold)
        rightAndWrite(purchase_id.date_approve.strftime("%d/%m/%Y"))
        breakAndWrite('Moneda:',bold)
        rightAndWrite(purchase_id.currency_id.name)

        #####Datos de la orden de compra
        addSalto()
        breakAndWrite("Orden de compras %s"%purchase_id.name,bold)
        breakAndWrite("Producto",bold)
        rightAndWrite("Cantidad",bold)
        rightAndWrite("Costo unit. origen %s"%purchase_id.currency_id.name,bold)
        rightAndWrite("Total origen %s"%purchase_id.currency_id.name,bold)
       
        for i in purchase_id.order_line:
            breakAndWrite(i.product_id.display_name)
            rightAndWrite(i.product_qty,numerico)
            rightAndWrite(i.price_unit,numerico)
            rightAndWrite(i.price_total,numerico)
        
        # Se obtienen los landed costs
        landed=self.env['stock.landed.cost'].search([('state','=','done'),('picking_ids','in',picking_id.id)])
        if not landed:
            raise exceptions.ValidationError("No se han cargado costos en destino para esta importación")
        # Se obtiene el asiento contable del picking
        picking_move_id=self.env['account.move'].search([('ref','ilike',picking_id.name)])
        tipo_cambio_picking=0
        if picking_move_id and sec_currency_id:
            tipo_cambio_picking=picking_move_id.line_ids[0].tipo_cambio


        #Costos aplicados
        addSalto()
        breakAndWrite("Costos aplicados",bold)
        breakAndWrite("Descripción",bold)
        rightAndWrite("Monto %s"%currency_id.name,bold)
        if sec_currency_id:
            rightAndWrite("Monto %s"%sec_currency_id.name,bold)
            rightAndWrite("Cotización",bold)

        breakAndWrite("Recepción %s"%picking_id.name)
        total_picking=0
        total_local=0
        total_usd=0
        for p in picking_id.move_ids:
            total_picking=total_picking+(p.price_unit*p.quantity_done)
        total_local=total_local+total_picking
        if sec_currency_id:
            total_usd=total_usd+(total_picking/tipo_cambio_picking)
        rightAndWrite(total_picking,numerico)
        if sec_currency_id:
            rightAndWrite(total_picking/tipo_cambio_picking,numerico_float)
            rightAndWrite(tipo_cambio_picking,numerico_float)
        for l in landed.cost_lines:
            if sec_currency_id:
                tipo_cambio_asiento=l.cost_id.account_move_id.line_ids[0].tipo_cambio
            breakAndWrite(l.name)
            rightAndWrite(l.price_unit,numerico_float)
            total_local=total_local+l.price_unit
            if sec_currency_id:
                rightAndWrite(l.price_unit/tipo_cambio_asiento,numerico_float)
                total_usd=total_usd+(l.price_unit/tipo_cambio_asiento)
                rightAndWrite(tipo_cambio_asiento,numerico_float)

        breakAndWrite("Total",bold)
        rightAndWrite(total_local,numerico_total)
        if sec_currency_id:
            rightAndWrite(total_usd,numerico_total_float)

        #Recepción
        addSalto()
        breakAndWrite("Recepción %s más costos en destino"%picking_id.name,bold)
        breakAndWrite("Producto",bold)
        rightAndWrite("Cantidad",bold)
        rightAndWrite("Costo unit. %s"%currency_id.name,bold)
        rightAndWrite("Costo total %s"%currency_id.name,bold)
        rightAndWrite("Costos aplicados unit. %s"%currency_id.name,bold)
        rightAndWrite("Costos aplicados %s"%currency_id.name,bold)
        rightAndWrite("Costo unit. final %s"%currency_id.name,bold)
        rightAndWrite("Costo final total %s"%currency_id.name,bold)
        if sec_currency_id:
            addRight()
            rightAndWrite("Costo unit. %s"%sec_currency_id.name,bold)
            rightAndWrite("Costo total %s"%sec_currency_id.name,bold)
            rightAndWrite("Costos aplicados unit. %s"%sec_currency_id.name,bold)
            rightAndWrite("Costos totales aplicados %s"%sec_currency_id.name,bold)
            rightAndWrite("Costo unit. final %s"%sec_currency_id.name,bold)
            rightAndWrite("Costo final total %s"%sec_currency_id.name,bold)
           
        for i in picking_id.move_ids:
            breakAndWrite(i.product_id.display_name)
            rightAndWrite(i.quantity_done,numerico)
            rightAndWrite(i.price_unit,numerico)
            rightAndWrite(i.price_unit * i.quantity_done,numerico)
            costos_adicionales=sum(landed.valuation_adjustment_lines.filtered(lambda x:x.product_id==i.product_id).mapped('additional_landed_cost'))
            rightAndWrite(costos_adicionales/i.quantity_done,numerico_float)
            rightAndWrite(costos_adicionales,numerico_float)
            costo_final=i.price_unit +(costos_adicionales/i.quantity_done)
            rightAndWrite(costo_final,numerico_float)
            rightAndWrite(costo_final*i.quantity_done,numerico_float)
            addRight()
            if sec_currency_id:
                rightAndWrite(i.price_unit/tipo_cambio_picking,numerico_float)
                rightAndWrite((i.price_unit * i.quantity_done)/tipo_cambio_picking,numerico_float)
                costos_adicionales=0
                for j in landed:
                    c=sum(j.valuation_adjustment_lines.filtered(lambda x:x.product_id==i.product_id).mapped('additional_landed_cost'))/ j.account_move_id.line_ids[0].tipo_cambio
                    costos_adicionales=costos_adicionales+c
                rightAndWrite((costos_adicionales/i.quantity_done),numerico_float)
                rightAndWrite(costos_adicionales,numerico_float)
                costo_final=(i.price_unit/tipo_cambio_picking) +((costos_adicionales/i.quantity_done))
                rightAndWrite(costo_final,numerico_float)
                rightAndWrite((costo_final*i.quantity_done),numerico_float)
                
