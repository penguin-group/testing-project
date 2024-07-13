# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from datetime import timedelta


class CalendarioFeriado(models.Model):
    _name = 'calendario.feriado'
    _description = 'Lista de feriados'
    _sql_constraints = [
        ('date_unique', 'UNIQUE (date)', 'Ya existe un feriado para esta fecha'),
    ]

    company_ids = fields.Many2many('res.company', string='Compañías')
    name = fields.Char(string='Descripción')
    date = fields.Date(string='Fecha')

    def check_feriado(self, date, company=False, discriminar_domingo=False):
        # rrhh_payroll/models/calendario_feriado.py
        feriado = False
        if not company:
            company = self.env.company
        if self.search([
            ('date', '=', date),
            '|',
            ('company_ids', '=', False),
            ('company_ids', '=', company.id)
        ]) or (not discriminar_domingo and date.weekday() == 6):
            feriado = True
        return feriado

    def sumar_dias_laborales(self, date, days_to_add, company=False, allowed_days=False):
        # rrhh_payroll/models/calendario_feriado.py
        if days_to_add:
            while days_to_add - 1:
                date += timedelta(days=1)
                if not self.check_feriado(date, company):
                    if allowed_days and str(date.weekday()) not in allowed_days:
                        continue
                    days_to_add -= 1
        return date

    def contar_dias_laborales(self, date_start, date_end, company=False, dias_corridos=False, allowed_days=False):
        # rrhh_payroll/models/calendario_feriado.py
        if date_start > date_end:
            return 0
        c = 0
        date = date_start
        while date <= date_end:
            if dias_corridos or not self.check_feriado(date, company):
                if dias_corridos or (allowed_days and str(date.weekday()) in allowed_days):
                    c += 1
            date += timedelta(days=1)
        return c
