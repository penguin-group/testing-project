# -*- coding: utf-8 -*-
from odoo import fields, models, api


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    currency_id = fields.Many2one(related="request_id.currency_id", string="Currency")
