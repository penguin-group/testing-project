from odoo import models, fields, api

class AccountReport(models.Model):
    _inherit = 'account.report'

    def _build_column_dict(
            self, col_value, col_data,
            options=None, currency=False, digits=1,
            column_expression=None, has_sublines=False,
            report_line_id=None,
    ):
        # Override this method to pass the currency selected by the user
        if options and options.get('currencies_selected_name'):
            currency = self.env['res.currency'].search([('name', '=', options['currencies_selected_name'])], limit=1)

        return super(AccountReport, self)._build_column_dict(
            col_value, col_data,
            options=options, currency=currency, digits=digits,
            column_expression=column_expression, has_sublines=has_sublines,
            report_line_id=report_line_id
        )