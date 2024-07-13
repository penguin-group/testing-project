from odoo import _, api, fields, models,exceptions



class SecondaryCurrencyAdjustment(models.Model):
    _name = 'secondary.currency.adjustment'
    _description = 'secondary.currency.adjustment'
    
    name=fields.Char(string="Número",default=lambda self:self.compute_number())
    currency_id=fields.Many2one('res.currency',string="Moneda de la compañia",default=lambda self:self.env.company.currency_id)
    secondary_currency_id=fields.Many2one('res.currency',string="Moneda secundaria",default=lambda self:self.env.company.secondary_currency_id)
    fecha=fields.Date(string="Fecha")
    fecha_anulacion=fields.Date(string="Fecha de anulación")
    rate=fields.Float(string="Tasa de cambio")
    line_ids=fields.One2many('secondary.currency.adjustment.line','adjustment_id')
    reference=fields.Char(string="Referencia")
    journal_id=fields.Many2one('account.journal',string="Diario",domain=[('type','=','general')])
    expense_account_id=fields.Many2one('account.account',string="Cuenta de gasto",domain=[('account_type','=','expense')])
    income_account_id=fields.Many2one('account.account',string="Cuenta de ingreso",domain=[('account_type','=','income')])
    move_id=fields.Many2one('account.move',string="Asiento de ajuste")
    reverse_move_id=fields.Many2one('account.move',string="Asiento de anulación")
    company_id=fields.Many2one('res.company',string="Compañia",default=lambda self:self.env.company)
    state=fields.Selection(string="Estado",selection=[('draft','Borrador'),('cancel','Cancelado'),('posted','Publicado')],default='draft')
    def compute_number(self):
        next_number=self.env['ir.sequence'].sudo().next_by_code('seq_adj_number')
        return next_number
    
    def button_create_move(self):
        line_ids=[]
        for line in self.line_ids.filtered(lambda x:x.difference<0):
            difference=abs(line.difference)
            l={
                'account_id':self.expense_account_id.id,
                'debit':0,
                'credit':0,
                'debit_ms':difference,
                'credit_ms':0,
                'balance_ms':difference,
            }
            line_ids.append((0,0,l))
            l2={
                'account_id':line.account_id.id,
                'debit':0,
                'credit':0,
                'debit_ms':0,
                'credit_ms':difference,
                'balance_ms':difference * -1,
            }
            line_ids.append((0,0,l2))
            
        for line in self.line_ids.filtered(lambda x:x.difference>0):
            difference=abs(line.difference)
            l={
                'account_id':self.income_account_id.id,
                'debit':0,
                'credit':0,
                'debit_ms':0,
                'credit_ms':difference,
                'balance_ms':difference * -1,
            }
            line_ids.append((0,0,l))
            l2={
                'account_id':line.account_id.id,
                'debit':0,
                'credit':0,
                'debit_ms':difference,
                'credit_ms':0,
                'balance_ms':difference,
            }
            line_ids.append((0,0,l2))
        
        if not self.move_id: 
            move_id=self.env['account.move'].create(
                {
                'journal_id':self.journal_id.id,
                'move_type':'entry',
                'date':self.fecha,
                'ref':self.reference,
                'line_ids':line_ids,
                'compute_secondary_values':False
                })
            if move_id:
                self.write({'move_id':move_id.id})
            
        else:
            self.move_id.button_draft()
            self.move_id.write({
                'journal_id':self.journal_id.id,
                'date':self.fecha,
                'ref':self.reference,
                'line_ids':line_ids
            })
        if not self.reverse_move_id and self.fecha_anulacion: 
            reverse_move_id=self.env['account.move'].create(
                {
                'journal_id':self.journal_id.id,
                'move_type':'entry',
                'date':self.fecha_anulacion,
                'ref':'Reversión %s'%self.reference,
                'line_ids':self.reverse(line_ids),
                'compute_secondary_values':False
                })
            if reverse_move_id:
                self.write({'reverse_move_id':reverse_move_id.id})
            
        elif self.reverse_move_id and self.fecha_anulacion:
            self.reverse_move_id.button_draft()
            self.reverse_move_id.write({
                'journal_id':self.journal_id.id,
                'date':self.fecha,
                'ref':self.reference,
                'line_ids':line_ids
            })
        elif self.reverse_move_id and not self.fecha_anulacion:
            self.reverse_move_id.button_draft()
            self.reverse_move_id.unlink()
        
        self.move_id._post()
        self.write({'state':'posted'})
        
        if self.reverse_move_id:
            self.reverse_move_id._post()
            
        

        return
    
    def reverse(self,line_ids):
        new_line_ids=[]
        for line in line_ids:
            account_id=line[2].get('account_id')
            if line[2].get('debit_ms')!=0:
                debit_ms=line[2].get('debit_ms')
                new_line_ids.append((0,0,{'account_id':account_id,'debit':0,'credit':0,'credit_ms':debit_ms,'debit_ms':0,'balance_ms':debit_ms*-1}))
            elif line[2].get('credit_ms')!=0:
                credit_ms=line[2].get('credit_ms')
                new_line_ids.append((0,0,{'account_id':account_id,'debit':0,'credit':0,'debit_ms':credit_ms,'credit_ms':0,'balance_ms':credit_ms}))
            else:
                new_line_ids.append((0,0,{'account_id':account_id,'debit':0,'credit':0,'credit_ms':0,'debit_ms':0,'balance_ms':0}))
        return new_line_ids
    def button_draft(self):
        if self.move_id:
            self.move_id.button_draft()
            self.move_id.unlink()
        if self.reverse_move_id:
            self.reverse_move_id.button_draft()
            self.reverse_move_id.unlink()
        self.write({'state':'draft'})
    def button_cancel(self):
        if self.move_id:
            self.move_id.button_cancel()
        if self.reverse_move_id:
            self.reverse_move_id.button_cancel()
        self.write({'state':'cancel'})
    def unlink(self):
        for i in self:
            if i.move_id or i.reverse_move_id:
                raise exceptions.UserError('No se puede eliminar una operación con asientos contables asociados')
    def button_calcular(self):
        self.populate_data()
    
    
    
    @api.depends('rate','fecha',)
    def compute_lines(self):
        rate=self.rate
        query=f""" 
            select s.account_id,s.cuenta,sum(s.balance) as operation_balance,sum(s.balance_ms) as operation_balance_ms,
            round((sum(s.balance)/{rate}),2) as current_rate_balance,
            --sum(s.difference) as difference
            (round((sum(s.balance)/{rate}),2)-sum(s.balance_ms)) as difference
            from (
 
            select aml.id,aa.name as Cuenta,aml.date,aml.account_id,aa.name,aml.currency_id,aml.amount_currency,aml.balance,aml.balance_ms,aml.tipo_cambio,
            case
                when aml.balance_ms is not null and aml.balance_ms != 0 then round((aml.balance/aml.balance_ms),2)
                else  1
            end as operation_rate,
            case
                when aml.balance_ms is not null and aml.balance_ms>0 then round((aml.balance / {rate}),2)
                else  1
            end as new_balance,
            round((aml.balance / {rate}),2) -balance_ms as difference
            from account_move_line aml
            inner join account_move am on aml.move_id=am.id
            inner join account_account aa on aml.account_id=aa.id
            where
            aml.balance_ms is not null and aml.balance_ms != 0
            and am.state='posted'
            and aml.date <= '{self.fecha.strftime('%Y-%m-%d')}'
            and aml.account_id in 
            (select id from account_account where (currency_id ={self.env.company.currency_id.id} or currency_id is null) and company_id={self.env.company.id} and account_type not in ('income','income_other','expense','expense_depreciation','expense_direct_cost'))
            ) as s group by s.account_id,s.cuenta order by s.cuenta
        """
        self._cr.execute(query)
        res=self._cr.fetchall()
        return res
        
    def populate_data(self):
        self.write({'line_ids':[(5,0,0)]})
        data=self.compute_lines()
        line_ids=[]
        for d in data:
            line={
                'account_id':d[0],
                'operation_balance':d[2],
                'operation_balance_ms':d[3],
                'current_rate_balance':d[4],
                'difference':d[5],
            }
            line_ids.append((0,0,line))
        self.line_ids=line_ids
    
class SecondaryCurrencyAdjustmentLine(models.Model):
    _name = 'secondary.currency.adjustment.line'
    _description = 'secondary.currency.adjustment.line'
    
    adjustment_id=fields.Many2one('secondary.currency.adjustment')
    account_id=fields.Many2one('account.account',string="Cuenta")
    currency_id=fields.Many2one('res.currency',related="adjustment_id.currency_id")
    secondary_currency_id=fields.Many2one('res.currency',related="adjustment_id.secondary_currency_id")
    operation_balance=fields.Monetary(string="Monto moneda primaria",currency_field="currency_id")
    operation_balance_ms=fields.Monetary(string="Monto moneda sec.",currency_field="secondary_currency_id")
    current_rate_balance=fields.Monetary(string="Monto moneda sec. cambio actual",currency_field="secondary_currency_id")
    difference=fields.Monetary(string="Monto ajuste",currency_field="secondary_currency_id")
