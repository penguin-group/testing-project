# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ConsolidationCompanyPeriod(models.Model):
    _inherit = "consolidation.company_period"

    def _get_total_balance_and_audit_lines(self, consolidation_account):
        """
        Get the total balance of all the move lines "linked" to this company and a given consolidation account
        :param consolidation_account: the consolidation account
        :return: the total balance as a float and the
        :rtype: tuple
        """
        self.ensure_one()
        domain = self._get_move_lines_domain(consolidation_account)
        res = self.env['account.move.line']._read_group(domain, ['balance_cs:sum', 'id:array_agg'], [])
        return res[0]['balance_cs'] or 0.0, res[0]['id'] or []
