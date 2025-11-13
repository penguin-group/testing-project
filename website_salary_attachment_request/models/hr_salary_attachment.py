from odoo import fields, models, _


class HrSalaryAttachment(models.Model):
    _inherit = 'hr.salary.attachment'

    state = fields.Selection(
        selection_add=[('to_check', _('To Check'))],
        ondelete={'to_check': 'set default'},
    )

