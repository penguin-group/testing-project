from odoo import _, api, fields, models, exceptions

from datetime import timedelta


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    compute_secondary_values=fields.Boolean(default=True,copy=False)

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft)
        for move in self:
            for line in move.line_ids:
                if move.compute_secondary_values:
                    line.compute_secondary_values()
                line.compute_consolidated_values()
            move.corregir_saldos_desbalanceados_ms()
        return res

    def corregir_saldos_desbalanceados_ms(self):
        for move in self:
            suma_debito = abs(sum(move.line_ids.mapped('debit_cs')))
            suma_credito = abs(sum(move.line_ids.mapped('credit_cs')))
            dif = suma_debito - suma_credito
            if dif != 0 and dif > 0:
                lines = move.line_ids.filtered(lambda x: x.credit > 0)
                lines[0].write({'credit_cs': lines[0].credit_cs + dif, 'credit_ms': lines[0].credit_ms + dif, 'balance_cs': lines[0].balance_cs - dif,
                                'balance_ms': lines[0].balance_ms - dif})
            elif dif != 0 and dif < 0:
                lines = move.line_ids.filtered(lambda x: x.debit > 0)
                lines[0].write({'debit_cs': lines[0].debit_cs - dif, 'debit_ms': lines[0].debit_ms - dif, 'balance_cs': lines[0].balance_cs + (dif * -1),
                                'balance_ms': lines[0].balance_ms + + (dif * -1)})


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    secondary_currency_id = fields.Many2one(
        "res.currency", string="Moneda secundaria",relation="move_line_currency_sec",)
    consolidated_currency_id=fields.Many2one('res.currency',relation="move_line_currency_cons", string="Moneda consolidada")
    
    tipo_cambio = fields.Float(string="Cotización")
    debit_ms = fields.Monetary(
        string="Débito (MS)", currency_field="secondary_currency_id",default=0)
    credit_ms = fields.Monetary(
        string="Crédito (MS)", currency_field="secondary_currency_id",default=0)
    balance_ms = fields.Monetary(
        string="Saldo (MS)", currency_field="secondary_currency_id",default=0)
    
    debit_cs = fields.Monetary(
        string="Débito (consolidado)", currency_field="consolidated_currency_id",default=0)
    credit_cs = fields.Monetary(
        string="Crédito (consolidado)", currency_field="consolidated_currency_id",default=0)
    balance_cs = fields.Monetary(
        string="Saldo (consolidado)", currency_field="consolidated_currency_id",default=0)

    def compute_secondary_values(self):
        secondary_currency_id = self.env.company.secondary_currency_id
        if not secondary_currency_id:
            return
        if secondary_currency_id == self.currency_id:
            tipo_cambio = 0
            if self.balance and self.amount_currency:
                tipo_cambio = abs(self.balance) / abs(self.amount_currency)
        else:
            tipo_cambio = secondary_currency_id.rate_ids.filtered(lambda x: x.name <= self.date)
            if tipo_cambio:
                tipo_cambio = round(tipo_cambio[0].inverse_company_rate,2)
            if not tipo_cambio:
                raise exceptions.ValidationError('No existe un tipo de cambio definido para la fecha %s'%self.date)
        if tipo_cambio>0:
            debit_ms = round(self.debit / tipo_cambio,2)
            credit_ms = round(self.credit / tipo_cambio,2)
            balance_ms = round(self.balance / tipo_cambio,2)
        else:
            debit_ms = 0
            credit_ms = 0
            balance_ms = 0
        self.write({'debit_ms': debit_ms,
                    'credit_ms': credit_ms,
                    'secondary_currency_id': secondary_currency_id.id,
                    'tipo_cambio': tipo_cambio,
                    'balance_ms': balance_ms})

    def compute_consolidated_values(self):
        currency_id=self.env.company.currency_id
        secondary_currency_id=self.env.company.secondary_currency_id
        cs_currency_id=self.env.company.consolidated_currency_id
        
        
        if cs_currency_id and currency_id and cs_currency_id == currency_id:
            self.write({
                        'consolidated_currency_id':cs_currency_id.id,
                        'debit_cs':self.debit,
                        'credit_cs':self.credit,
                        'balance_cs':self.balance,
                        })
        
        elif cs_currency_id and secondary_currency_id and cs_currency_id == secondary_currency_id:
            self.write({
                        'consolidated_currency_id':cs_currency_id.id,
                        'debit_cs':self.debit_ms,
                        'credit_cs':self.credit_ms,
                        'balance_cs':self.balance_ms,
                        })
        else:
            return