from odoo import _, api, fields, models




class ResCompany(models.Model):
    _inherit = 'res.company'

    secondary_currency_id=fields.Many2one('res.currency',string="Moneda secundaria",relation="company_currency_sec")
    consolidated_currency_id=fields.Many2one('res.currency',string="Moneda de consolidación",relation="company_currency_cons")
    
    
    
    def compute_sec_cons_values(self):
        move_ids=self.env['account.move'].search([('company_id','=',self.env.company.id),('state','=','posted')])
        for move in move_ids:
            for line in move.line_ids:
                line.compute_secondary_values()
                line.compute_consolidated_values()
        partial_reconcile_ids=self.env['account.partial.reconcile'].search([('company_id','=',self.env.company.id)])
        for partial in partial_reconcile_ids:
            partial.compute_amount_cs()
        
