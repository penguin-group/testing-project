from odoo import models, fields, api, _


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    project_id = fields.Many2one("project.project", string="Project")
    request_assistance = fields.Boolean(string="Request Assistance")
    off_budget = fields.Boolean(string="Off-Budget", tracking=True)
    
    # Redefine the field to remove the 'related' attribute.
    # We make it a standard Many2one field that stores its own value.
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related=False,
        required=True,
        store=True,
        readonly=False,
        default=lambda self: self.env.company.currency_id.id
    )

    currency_old = fields.Char()

    def _link_attachments_to_purchase_order(self, purchase_order):
        """
        Create new attachment records for the purchase order that reference
        the same stored files from the purchase request attachments.
        """
        attachments = self.env["ir.attachment"].search(
            [("res_model", "=", "purchase.request"), ("res_id", "=", self.id)]
        )

        for attachment in attachments:
            # Create new attachment record but reference the same store_fname
            self.env["ir.attachment"].create(
                {
                    "name": attachment.name,
                    "type": attachment.type,
                    "res_model": "purchase.order",
                    "res_id": purchase_order.id,
                    "store_fname": attachment.store_fname,  # Reference same file
                    "mimetype": attachment.mimetype,
                    "datas": attachment.datas,  # This references the same file content
                }
            )

    @api.depends("line_ids", "line_ids.estimated_cost")
    def _compute_estimated_cost(self):
        """Fully override this method because the original does not include the quantity in the computation."""
        for rec in self:
            rec.estimated_cost = sum(
                line.estimated_cost * line.product_qty for line in rec.line_ids
            )

    def write(self, vals):
        """Store the currency in an additional field to use it on currency change"""
        if "currency_id" in vals:
            for record in self:
                if record.currency_id:
                    vals["currency_old"] = vals["currency_id"]
        return super().write(vals)

    @api.onchange("currency_id")
    def _onchange_currency_id(self):    
        for record in self:
            if record.currency_old and record.currency_id.id != int(record.currency_old):
                currency_old = self.env["res.currency"].browse(int(record.currency_old))
                if currency_old:
                    # Convert estimated costs in line items to the new currency
                    for line in record.line_ids:
                        line.estimated_cost = currency_old._convert(
                            line.estimated_cost,
                            record.currency_id,
                            record.company_id,
                            record.date_start or fields.Date.today(),
                        )

    def action_cancel_with_confirmation(self):
        """Wizard to double-check before cancelling a Purchase Request."""
        self.ensure_one()

        modal_title = _('Double-check before resetting') \
            if 'cancelling_from_reset_button' in self._context \
            else _('Double-check before rejecting')

        view_id = self.env.ref('pisa_purchase.view_purchase_request_reset_wizard_form').id \
            if 'cancelling_from_reset_button' in self._context \
            else self.env.ref('pisa_purchase.view_purchase_request_reject_wizard_form').id

        return {
            'name':modal_title,
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.request.cancel.wizard',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'default_purchase_request_id': self.id},
        }
