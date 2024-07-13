from odoo import _, api, fields, models



class AccountPartialReconcile(models.Model):
    _inherit = 'account.partial.reconcile'


    amount_cs=fields.Float(string="Amount CS",default=0)
    
    
    
    def compute_amount_cs(self):
        cs_currency_id=self.env.company.consolidated_currency_id
        amount_cs=0
        balance_debit=abs(self.debit_move_id.balance)
        balance_credit=abs(self.credit_move_id.balance)
        if self.amount==balance_debit:
            amount_cs=abs(self.debit_move_id.balance_cs)
                
        elif self.amount==balance_credit:
            amount_cs=abs(self.credit_move_id.balance_cs)
        else:
            amount_cs=0
        self.with_context(compute_amount_cs=True).write({'amount_cs':amount_cs})
    
    def write(self,vals):
        res=super(AccountPartialReconcile,self).write(vals)
        if not self._context.get('compute_amount_cs'):
            for record in self:
                record.compute_amount_cs()
        return res
    
    @api.model
    def create(self,vals):
        res=super(AccountPartialReconcile,self).create(vals)
        res.compute_amount_cs()
        return res
                
            
        
        