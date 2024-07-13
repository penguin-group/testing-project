# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PatronalPatronal(models.Model):
    _name = 'res.company.patronal'
    _description = 'Número de Patronal especificado por las instituciones correspondientes'
    _sql_constraints = [
        ('res_company_patronal_number_unique', 'unique(number)', "Éste número de patronal ya existe"),
    ]

    name = fields.Char(string='Nombre', required=True)
    actividad = fields.Char(string='Actividad')
    company_id = fields.Many2one('res.company', string='Compañia', required=True)
    number = fields.Char(string='Número', required=True)
    patronal_tipo = fields.Selection(selection=[('mtess', 'MTESS'), ('ips', 'IPS')], string='Tipo', required=True)

    # patronal_mtess_id = fields.Many2one('res.company.patronal', required=True)

    def _get_contratos_count(self):
        for this in self:
            this.contratos_count = len(self.env['hr.contract'].search([
                '|',
                ('patronal_ips_id', '=', this.id),
                ('patronal_mtess_id', '=', this.id),
            ]))

    contratos_count = fields.Integer(string='Contratos', compute='_get_contratos_count')

    # def action_view_contracts(self):
    #     action = self.env.ref('hr_payroll.action_hr_contract_repository').read()[0]
    #     action['domain'] = [('id', 'in', self.env['hr.contract'].search([
    #         '|',
    #         '|',
    #         ('patronal_amh_id', '=', self.id),
    #         ('patronal_ips_id', '=', self.id),
    #         ('patronal_mtess_id', '=', self.id),
    #     ]).ids)]
    #     action['context'] = {
    #         'search_default_group_by_company': False,
    #     }
    #     return action
