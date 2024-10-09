from odoo import api, fields, models, tools, _


class Currency(models.Model):
    _inherit = 'res.currency'

    def _get_rates(self, company, date, rate_type='selling'):
        # Override original method to add the rate type to get
        if not self.ids:
            return {}
        self.env['res.currency.rate'].flush_model(['rate', 'currency_id', 'company_id', 'name', 'rate_type'])
        query = """SELECT c.id,
                          COALESCE((SELECT r.rate FROM res_currency_rate r
                                  WHERE r.currency_id = c.id 
                                    AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                                    AND (r.rate_type = %s OR r.rate_type IS NULL)
                               ORDER BY r.company_id, r.name DESC
                                  LIMIT 1), 1.0) AS rate
                   FROM res_currency c
                   WHERE c.id IN %s"""
        self._cr.execute(query, (date, company.root_id.id, rate_type, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        return currency_rates
    

class CurrencyRate(models.Model):
    _inherit = 'res.currency.rate'


    rate_type = fields.Selection([
        ('buying', 'Buying'),
        ('selling', 'Selling')
    ], string='Rate Type', default='selling')

    _sql_constraints = [
        ('unique_name_per_day', 'unique (name,rate_type,currency_id,company_id)', 'Only one currency rate per day allowed!'),
    ]
    