from odoo import fields, api, models, exceptions, tools
import datetime, logging

_logger = logging.getLogger(__name__)


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    state = fields.Selection(tracking=True)

    def action_draft(self):
        self.slip_ids.action_payslip_cancel()
        return super().action_draft()
