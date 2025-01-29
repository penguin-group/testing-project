from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountReport(models.Model):
    _inherit = 'account.report'

    def _get_lines(self, options, all_column_groups_expression_totals=None, warnings=None):
        lines = super(AccountReport, self)._get_lines(options, all_column_groups_expression_totals, warnings)
        lines = self._create_analytic_hierarchy(lines, options)
        return lines


    def _create_analytic_hierarchy(self, lines, options):
        """Compute the hierarchy based on analytic accounts.

        This method takes the lines resulting from _create_hierarchy and organizes them
        into a hierarchy based on analytic accounts.
        """
        if not lines:
            return lines

        def create_analytic_hierarchy_line(analytic_account, column_totals, level, parent_id, cnt=0):
            line_id = self._get_generic_line_id('account.analytic.account', analytic_account.id, cnt, parent_id)
            unfolded = line_id in options.get('unfolded_lines') or options['unfold_all']
            name = analytic_account.display_name if analytic_account else _('(No Analytic Account)')
            columns = []
            for column_total, column in zip(column_totals, options['columns']):
                columns.append(self._build_column_dict(column_total, column, options=options))
            return {
                'id': line_id,
                'name': name,
                'title_hover': name,
                'unfoldable': True,
                'unfolded': unfolded,
                'level': level,
                'parent_id': parent_id,
                'columns': columns,
            }

        zero_level_lines = []
        other_lines = []
        new_lines = []

        # Adjust the levels of the existing lines
        for line in lines:
            if line['level'] > 0:
                line['level'] += 1
                other_lines.append(line)
            else:
                zero_level_lines.append(line)

        olcnt = 0
        for zero_level in zero_level_lines:
            new_lines.append(zero_level)
            cnt = 0
            for analytic_account in self.env['account.analytic.account'].browse(options.get('analytic_accounts')):
                cnt += 1
                one_level_line = create_analytic_hierarchy_line(analytic_account, [0] * len(options['columns']), 1, zero_level['id'], cnt)
                new_lines.append(one_level_line)
                for line in other_lines:
                    olcnt += 1
                    line_copy = line.copy()
                    line_copy['parent_id'] = one_level_line['id']
                    line_copy['id'] = self._get_generic_line_id('account.report.line', None, olcnt, one_level_line['id'])
                    new_lines.append(line_copy)

        return new_lines