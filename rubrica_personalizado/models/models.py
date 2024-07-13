# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class rubrica_personalizado(models.Model):
#     _name = 'rubrica_personalizado.rubrica_personalizado'
#     _description = 'rubrica_personalizado.rubrica_personalizado'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
