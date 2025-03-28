from odoo import models, fields, api
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import AccessError, UserError, ValidationError, RedirectWarning

class AccountAccount(models.Model):
    _inherit = 'hr.expense.sheet'

    invoice_id = fields.Many2one("account.move", string="Factura", readonly=True)


    def action_create_invoice(self):


        self.ensure_one()  # Asegura que solo hay una hoja de gastos seleccionada

        if self.invoice_id:
            raise UserError(_("An invoice already exists linked to this expense report."))

        hr_expense = self.env["hr.expense"].search([("sheet_id", "=", self.id)], limit=1)
        partner_id = hr_expense.vendor_id.id


        if not partner_id:
            raise UserError(_("The expense does not have an assigned supplier."))


        journal = self.env["account.journal"].search([("type", "=", "purchase")], limit=1)

        if not journal:
            raise UserError(_("There is no shopping journal set up."))


        invoice_vals = {
            "move_type": "in_invoice",  # Factura de proveedor
            "partner_id": partner_id,  # Proveedor
            "invoice_date": fields.Date.today(),
            "journal_id": journal.id,
            "currency_id": self.currency_id.id,
            "invoice_line_ids": [],
        }


        invoice_lines = []
        for expense in self.expense_line_ids:
            if not expense.product_id:
                raise UserError(_("Expense '%s' does not have an associated product.") % expense.name)

            line_vals = {
                "product_id": expense.product_id.id,
                "name": expense.name,
                "quantity": 1,
                "price_unit": expense.total_amount,
                "account_id": expense.product_id.property_account_expense_id.id or expense.product_id.categ_id.property_account_expense_categ_id.id,
            }
            invoice_lines.append((0, 0, line_vals))

        invoice_vals["invoice_line_ids"] = invoice_lines

        invoice = self.env["account.move"].create(invoice_vals)

        self.write({"invoice_id": invoice.id})

        return {
            "name": _("Factura creada"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": invoice.id,
        }

