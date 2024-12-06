from odoo import models, fields, api, _
import datetime
import logging

_logger = logging.getLogger(__name__)


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    def fix_depreciation_moves(self):
        cnt = 0
        total = len(self)
        for asset in self:
            cnt += 1
            percentage_completed = (cnt / total) * 100
            _logger.info(f"{percentage_completed:.2f}% Completed")
            depreciation_moves = asset.depreciation_move_ids.filtered(lambda m: m.date >= datetime.date(2024, 11, 1))
            for move in depreciation_moves:
                move.recompute_balance()
                