from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

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
    analytic_account_vertical = fields.Boolean('Analytic Account Vertical', help='If checked, the analytic accounts will be grouped vertically in the report.')

    @api.constrains('filter_analytic_groupby', 'analytic_account_vertical', 'root_report_id', 'filter_analytic')
    def _check_filter_analytic_groupby(self):
        for record in self:
            if record.filter_analytic_groupby and record.analytic_account_vertical:
                raise ValidationError(_('The fields "Analytic Group By" and "Analytic Account Vertical" cannot both be selected.'))
            if record.analytic_account_vertical and not record.root_report_id:
                raise ValidationError(_('The field "Root Report" is mandatory when "Analytic Account Vertical" is selected.'))
            if record.analytic_account_vertical and not record.filter_analytic:
                raise ValidationError(_('The field "Analytic Filter" must be selected when "Analytic Account Vertical" is selected.'))

    def get_report_information(self, options):
        options_analytic_accounts = options.get('analytic_accounts')
        if self.analytic_account_vertical and self.root_report_id and options_analytic_accounts:
            self.line_ids.unlink()
            analytic_accounts = self.env['account.analytic.account'].browse(options_analytic_accounts)
            self._create_lines_with_analytic(analytic_accounts)
        return super(AccountReport, self).get_report_information(options)
    
    def _create_lines_with_analytic(self, analytic_accounts):
        seq = 0
        line_cache = {}
        for line in self.root_report_id.line_ids:
            seq += 10
            new_line = line.copy({'report_id': self.id, 'sequence': seq})
            line_cache[line.id] = new_line.id
            new_line.write({'parent_id': line_cache.get(line.parent_id.id)})

            # Update level
            if new_line.hierarchy_level != 0:
                new_line.hierarchy_level += 1
            
            if 'domain' in line.expression_ids.mapped('engine'):
                new_line.write({
                    'groupby': False, 
                    'user_groupby': False,
                })
                # Generate additional lines for analytic accounts
                vals = []
                total_formula = ''
                for analytic_account in analytic_accounts:
                    code = new_line.code + '_' + str(analytic_account.id)
                    expr_formula = line.expression_ids[0].formula
                    expr_formula = f"{expr_formula[:-1]}, ('analytic_distribution', 'in', [{analytic_account.id}])]"
                    expr_vals = {
                        'label': 'balance',
                        'engine': 'domain',
                        'formula': expr_formula,
                        'subformula': 'sum',
                    }
                    vals.append({
                        'report_id': self.id,
                        'name': analytic_account.display_name,
                        'code': code,
                        'parent_id': new_line.id,
                        'hierarchy_level': new_line.hierarchy_level + 2,
                        'sequence': seq + 1,
                        'foldable': True,
                        'hide_if_zero': True,
                        'groupby': line.groupby,
                        'expression_ids': [(0, 0, expr_vals)]
                    })
                    total_formula += f' + {code}.balance' if total_formula else f'{code}.balance'
                self.env['account.report.line'].create(vals)                    
                self.env['account.report.expression'].create({
                    'report_line_id': new_line.id,
                    'label': 'balance',
                    'engine': 'aggregation',
                    'formula': total_formula
                })
            else:
                for expr in line.expression_ids:
                    expr.copy({'report_line_id': new_line.id})
