from odoo import api, fields, models, tools, _


class Currency(models.Model):
    _inherit = 'res.currency'

    buying_rate = fields.Float(compute='_compute_current_rate', string='Current Buying Rate', digits=0,
                        help='The buying rate of the currency to the currency of rate 1.')
    buying_inverse_rate = fields.Float(compute='_compute_current_rate', digits=0, readonly=True,
                                help='The currency of rate 1 to the buying rate of the currency.')
    buying_rate_string = fields.Char(compute='_compute_current_rate')

    def _get_buying_rates(self, company, date):
        if not self.ids:
            return {}
        self.env['res.currency.rate'].flush_model(['buying_rate', 'currency_id', 'company_id', 'name'])
        query = """SELECT c.id,
                          COALESCE((SELECT r.buying_rate FROM res_currency_rate r
                                  WHERE r.currency_id = c.id AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                               ORDER BY r.company_id, r.name DESC
                                  LIMIT 1), 1.0) AS buying_rate
                   FROM res_currency c
                   WHERE c.id IN %s"""
        self._cr.execute(query, (date, company.root_id.id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        return currency_rates

    @api.depends('rate_ids.rate')
    @api.depends_context('to_currency', 'date', 'company', 'company_id')
    def _compute_current_rate(self):
        # Override original method to compute values for buying rate fields
        date = self._context.get('date') or fields.Date.context_today(self)
        company = self.env['res.company'].browse(self._context.get('company_id')) or self.env.company
        company = company.root_id
        to_currency = self.browse(self.env.context.get('to_currency')) or company.currency_id
        # the subquery selects the last rate before 'date' for the given currency/company
        currency_rates = (self + to_currency)._get_rates(self.env.company, date)
        currency_buying_rates = (self + to_currency)._get_buying_rates(self.env.company, date)
        for currency in self:
            currency.rate = (currency_rates.get(currency.id) or 1.0) / currency_rates.get(to_currency.id)
            currency.buying_rate = (currency_buying_rates.get(currency.id) or 1.0) / currency_buying_rates.get(to_currency.id)
            currency.inverse_rate = 1 / currency.rate
            currency.buying_inverse_rate = 1 / currency.buying_rate
            if currency != company.currency_id:
                currency.rate_string = '1 %s = %.6f %s' % (to_currency.name, currency.rate, currency.name)
                currency.buying_rate_string = '1 %s = %.6f %s' % (to_currency.name, currency.buying_rate, currency.name)
            else:
                currency.rate_string = ''
                currency.buying_rate_string = ''
    
    @api.model
    def _get_buying_conversion_rate(self, from_currency, to_currency, company=None, date=None):
        if from_currency == to_currency:
            return 1
        company = company or self.env.company
        date = date or fields.Date.context_today(self)
        return from_currency.with_company(company).with_context(to_currency=to_currency.id, date=str(date)).buying_inverse_rate
    

class CurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    buying_rate = fields.Float(
        digits=0,
        group_operator="avg",
        help='The buying rate of the currency to the currency of rate 1',
        string='Buying Technical Rate'
    )
    buying_company_rate = fields.Float(
        digits=0,
        compute="_compute_buying_company_rate",
        inverse="_inverse_buying_company_rate",
        group_operator="avg",
        help="The buying currency of rate 1 to the rate of the currency.",
    )
    buying_inverse_company_rate = fields.Float(
        digits=0,
        compute="_compute_buying_inverse_company_rate",
        inverse="_inverse_buying_inverse_company_rate",
        group_operator="avg",
        help="The buying rate of the currency to the currency of rate 1 ",
    )

    def _sanitize_vals(self, vals):
        vals = super(CurrencyRate, self)._sanitize_vals(vals)
        if 'buying_inverse_company_rate' in vals and ('buying_company_rate' in vals or 'buying_rate' in vals):
            del vals['buying_inverse_company_rate']
        if 'buying_company_rate' in vals and 'buying_rate' in vals:
            del vals['buying_company_rate']
        return vals

    def write(self, vals):
        self.env['res.currency'].invalidate_model(['buying_inverse_rate'])
        return super().write(self._sanitize_vals(vals))

    @api.model_create_multi
    def create(self, vals_list):
        self.env['res.currency'].invalidate_model(['buying_inverse_rate'])
        return super().create([self._sanitize_vals(vals) for vals in vals_list])

    def _get_last_buying_rates_for_companies(self, companies):
        return {
            company: company.currency_id.rate_ids.sudo().filtered(lambda x: (
                x.buying_rate
                and x.company_id == company or not x.company_id
            )).sorted('name')[-1:].buying_rate or 1
            for company in companies
        }

    @api.depends('currency_id', 'company_id', 'name')
    def _compute_buying_rate(self):
        for currency_rate in self:
            currency_rate.buying_rate = currency_rate.buying_rate or currency_rate._get_latest_rate().buying_rate or 1.0
    
    @api.depends('buying_rate', 'name', 'currency_id', 'company_id', 'currency_id.rate_ids.buying_rate')
    @api.depends_context('company')
    def _compute_buying_company_rate(self):
        last_rate = self.env['res.currency.rate']._get_last_buying_rates_for_companies(self.company_id | self.env.company.root_id)
        for currency_rate in self:
            company = currency_rate.company_id or self.env.company.root_id
            currency_rate.buying_company_rate = (currency_rate.buying_rate or currency_rate._get_latest_rate().buying_rate or 1.0) / last_rate[company]

    @api.onchange('buying_company_rate')
    def _inverse_buying_company_rate(self):
        last_rate = self.env['res.currency.rate']._get_last_buying_rates_for_companies(self.company_id | self.env.company.root_id)
        for currency_rate in self:
            company = currency_rate.company_id or self.env.company.root_id
            currency_rate.buying_rate = currency_rate.buying_company_rate * last_rate[company]

    @api.depends('buying_company_rate')
    def _compute_buying_inverse_company_rate(self):
        for currency_rate in self:
            if not currency_rate.buying_company_rate:
                currency_rate.buying_company_rate = 1.0
            currency_rate.buying_inverse_company_rate = 1.0 / currency_rate.buying_company_rate

    @api.onchange('buying_inverse_company_rate')
    def _inverse_buying_inverse_company_rate(self):
        for currency_rate in self:
            if not currency_rate.buying_inverse_company_rate:
                currency_rate.buying_inverse_company_rate = 1.0
            currency_rate.buying_company_rate = 1.0 / currency_rate.buying_inverse_company_rate
    