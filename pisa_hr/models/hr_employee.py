from odoo import models, api, fields


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # Override the pin field to make it a computed field based on barcode
    pin = fields.Char(
        string="PIN", 
        groups="hr.group_hr_user", 
        copy=False,
        compute="_compute_pin",
        store=True,
        help="PIN used to Check In/Out in the Kiosk Mode of the Attendance application (if enabled in Configuration) and to change the cashier in the Point of Sale application.")

    @api.depends("barcode")
    def _compute_pin(self):
        for employee in self:
            employee.pin = employee.barcode or False
    