from odoo import models, fields, api, exceptions


class ResCompany(models.Model):
    _inherit = 'res.company'

    res90_imputes_irp_rsp_default = fields.Boolean(string="Impute IRP/RSP by default")