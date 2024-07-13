from odoo import _, api, fields, models

from datetime import timedelta
class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'


    secondary_currency_id=fields.Many2one('res.currency',default=lambda self:self.env.company.secondary_currency_id,string='Moneda secundaria')
    planned_amount_sec=fields.Monetary('Imp. previsto MS',currency_field='secondary_currency_id')
    practical_amount_sec=fields.Monetary('Imp. real MS',currency_field='secondary_currency_id',compute='_compute_practical_amount_sec')
    theoritical_amount_sec=fields.Monetary('Imp. teórico MS',currency_field='secondary_currency_id',compute='_compute_theoritical_amount_sec')
    percentage_sec=fields.Float(string='Logro MS',compute='_compute_percentage_sec')

    def _compute_practical_amount_sec(self):
        for line in self:
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = line.date_to
            date_from = line.date_from
            if line.analytic_account_id.id:
                analytic_line_obj = self.env['account.analytic.line']
                domain = [('account_id', '=', line.analytic_account_id.id),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ]
                if acc_ids:
                    domain += [('general_account_id', 'in', acc_ids)]

                where_query = analytic_line_obj._where_calc(domain)
                analytic_line_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT SUM(amount) from " + from_clause + " where " + where_clause

            else:
                aml_obj = self.env['account.move.line']
                domain = [('account_id', 'in',
                           line.general_budget_id.account_ids.ids),
                          ('date', '>=', date_from),
                          ('date', '<=', date_to),
                          ('parent_state', '=', 'posted')
                          ]
                where_query = aml_obj._where_calc(domain)
                aml_obj._apply_ir_rules(where_query, 'read')
                from_clause, where_clause, where_clause_params = where_query.get_sql()
                select = "SELECT sum(credit_ms)-sum(debit_ms) from " + from_clause + " where " + where_clause

            self.env.cr.execute(select, where_clause_params)
            line.practical_amount_sec = self.env.cr.fetchone()[0] or 0.0

    @api.depends('date_from', 'date_to')
    def _compute_theoritical_amount_sec(self):
        # beware: 'today' variable is mocked in the python tests and thus, its implementation matter
        today = fields.Date.today()
        for line in self:
            if line.paid_date:
                if today <= line.paid_date:
                    theo_amt = 0.00
                else:
                    theo_amt = line.planned_amount_sec
            else:
                if not line.date_from or not line.date_to:
                    line.theoritical_amount_sec = 0
                    continue
                # One day is added since we need to include the start and end date in the computation.
                # For example, between April 1st and April 30th, the timedelta must be 30 days.
                line_timedelta = line.date_to - line.date_from + timedelta(days=1)
                elapsed_timedelta = today - line.date_from + timedelta(days=1)

                if elapsed_timedelta.days < 0:
                    # If the budget line has not started yet, theoretical amount should be zero
                    theo_amt = 0.00
                elif line_timedelta.days > 0 and today < line.date_to:
                    # If today is between the budget line date_from and date_to
                    theo_amt = (elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.planned_amount_sec
                else:
                    theo_amt = line.planned_amount_sec
            line.theoritical_amount_sec = theo_amt

    def _compute_percentage_sec(self):
        for line in self:
            if line.theoritical_amount_sec != 0.00:
                line.percentage_sec = float((line.practical_amount_sec or 0.0) / line.theoritical_amount_sec)
            else:
                line.percentage_sec = 0.00
