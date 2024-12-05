from odoo import models, fields, api, _
import datetime


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    def fix_depreciation_moves(self):
        for asset in self:
            depreciation_moves = asset.depreciation_move_ids.filtered(lambda m: m.date >= datetime.date(2024, 11, 1))
            for move in depreciation_moves:
                move.recompute_balance()
                