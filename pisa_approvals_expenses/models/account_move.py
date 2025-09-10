from odoo import fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    approval_id = fields.Many2one('approval.request', string="Related approval request")

    def action_view_approval(self):
        self.ensure_one()
        approval_request = self.env['approval.request'].search([('related_vendor_bill', '=', self.id)])
        return {
            "type": "ir.actions.act_window",
            "res_model": "approval.request",
            "domain": [('id', 'in', approval_request.ids)],
            "name": _("Approval Request"),
            'view_mode': 'list,form',
        }
