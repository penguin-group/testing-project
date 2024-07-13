from odoo import api, fields, models


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    force_day_period_check = fields.Boolean('Forzar Periodo del Día', default=False)
    force_day_period = fields.Selection(selection=[('morning', 'Mañana'), ('afternoon', 'Tarde')], string='Periodo del día', default='morning')

    force_resource_calendar_id_check = fields.Boolean('Forzar Planeamiento de Asistencias', default=False)
    force_resource_calendar_id = fields.Many2one('resource.calendar', string='Planeamiento de Asistencias')

    @api.onchange('date', 'employee_id', 'force_day_period_check', 'force_day_period')
    def get_entrada_salida_planeada(self):
        # rrhh_personalizado/models/hr_attendance.py
        result = super(HrAttendance, self).get_entrada_salida_planeada()
        for this in self:
            if this.force_day_period_check or this.force_resource_calendar_id_check:
                day_period = this.day_period
                resource_calendar_id = this.resource_calendar_id
                if this.force_day_period_check:
                    day_period = this.force_day_period
                if this.force_resource_calendar_id_check:
                    resource_calendar_id = this.force_resource_calendar_id
                entrada_planeada = False
                salida_planeada = False
                if this.employee_id and this.date:
                    entrada_planeada = this.contract_id.get_entrada_planeada(this.date, day_period, resource_calendar_id)
                    salida_planeada = this.contract_id.get_salida_planeada(this.date, day_period, resource_calendar_id)
                this.entrada_planeada = entrada_planeada
                this.salida_planeada = salida_planeada
                this.day_period = day_period
                this.resource_calendar_id = resource_calendar_id
        return result
