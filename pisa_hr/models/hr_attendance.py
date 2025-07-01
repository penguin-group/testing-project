from odoo import api, models, fields


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    def import_attendance_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'import.attendance.records.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('pisa_hr.import_attendance_records_form').id,
            'target': 'new',
            'context': {'active_id': self.id}
        }