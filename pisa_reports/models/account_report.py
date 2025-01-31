from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountReport(models.Model):
    _inherit = 'account.report'

    analytic_account_vertical = fields.Boolean('Analytic Account Vertical', help='If checked, the analytic accounts will be grouped vertically in the report.')

    def _get_lines(self, options, all_column_groups_expression_totals=None, warnings=None):
        analytic_accounts = self.env['account.analytic.account'].browse(options.get('analytic_accounts_groupby'))
        if self.analytic_account_vertical and self.root_report_id and analytic_accounts:
            self._create_lines_with_analytic(analytic_accounts)
        lines = super(AccountReport, self)._get_lines(options, all_column_groups_expression_totals, warnings)
        return lines
    
    def _create_lines_with_analytic(self, analytic_accounts):
        self.line_ids.unlink()

        seq = 0
        line_cache = {}
        for line in self.root_report_id.line_ids:
            seq += 10
            new_line = line.copy({'report_id': self.id, 'code': line.code + '_A', 'sequence': seq})
            line_cache[line.id] = new_line.id
            new_line.write({'parent_id': line_cache.get(line.parent_id.id)})

            # Update level
            if new_line.hierarchy_level != 0:
                new_line.hierarchy_level += 1
            
            if 'domain' in line.expression_ids.mapped('engine'):
                new_line.write({'groupby': False, 'user_groupby': False})
                # Generate additional lines for analytic accounts
                vals = []
                for analytic_account in analytic_accounts:
                    vals.append({
                        'report_id': self.id,
                        'name': analytic_account.display_name,
                        'parent_id': new_line.id,
                        'hierarchy_level': new_line.hierarchy_level + 2,
                        'sequence': seq + 1,
                        'foldable': True,
                        'groupby': line.groupby,
                        # 'expression_ids': [(0, 0, expr.copy_data()[0]) for expr in line.expression_ids]
                    })
                self.env['account.report.line'].create(vals)
            # else:
            #     for expr in line.expression_ids:
            #         expr.copy({'report_line_id': new_line.id})
