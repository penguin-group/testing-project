from odoo import models, fields, _
from odoo.exceptions import UserError

class TicketValidationWizard(models.TransientModel):
    _name = 'ticket.validation.wizard'
    _description = 'Ticket Validation Wizard'

    input_field = fields.Char(string="Input Data", required=True)
    repair_order_id = fields.Many2one('repair.order', string="Repair Order", required=True)

    def proceed_action(self):
        if not self.input_field:
            raise UserError("You must enter data to continue.")

        lot = self.repair_order_id.lot_id

        if not lot:
            raise UserError("The product has no associated lot or serial number.")

        if self.input_field != lot.name:
            raise UserError(_("The entered data does not match the machine's Serial Number."))
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'repair.order',
            'view_mode': 'form',
            'res_id': self.repair_order_id.id,
            'target': 'current',
            'context': {
                'is_validated_temp': True
            }
        }

    def cancel_action(self):
        return {'type': 'ir.actions.act_window_close'}