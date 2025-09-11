from odoo import fields, models, _, api


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

    @api.depends('amount_residual', 'move_type', 'state', 'company_id', 'matched_payment_ids.state')
    def _compute_payment_state(self):
        super(AccountMove, self)._compute_payment_state()

        for move in self:
            if move.move_type == 'in_invoice' and move.payment_state == 'paid' and move.approval_id:
                move.approval_id.request_status = 'paid'
