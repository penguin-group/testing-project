# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    move_number = fields.Integer(string='Número de Asiento', index=True)

    def set_move_numbers(self):
        for company in self.env['res.company'].sudo().search([]):
            self.env.cr.execute("SELECT id FROM account_move WHERE company_id=%s AND state='posted' ORDER BY date,name,id" % company.id)
            account_move_ids = [x[0] for x in self.env.cr.fetchall()]
            sql_querys = ''
            move_number = 1
            for account_move_id in account_move_ids:
                sql_querys += 'UPDATE account_move SET move_number=%s WHERE id=%s AND (move_number!=%s OR move_number IS NULL);' % (
                    move_number, account_move_id, move_number
                )
                move_number += 1
            self.env.cr.execute(sql_querys)
