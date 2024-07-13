from odoo import api, fields, models, exceptions,_


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for this in self:
            # se verifica si no posee el permiso para confirmar
            if not this.env.user.has_group('permiso_personalizacion.check_validar_factura'):
                raise exceptions.ValidationError('No posee permisos para confirmar la factura.')
        return super(AccountMove, self).action_post() 