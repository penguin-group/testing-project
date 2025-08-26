from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RepairFault(models.Model):
    _name = 'repair.fault'
    _description = 'Types of Repair Faults'
    _rec_name = 'name'

    name = fields.Char(string="Failure name", required=True, index=True, translate=True)
    description = fields.Text(string="Description", translate=True)
    display_name = fields.Char(string="Full name", compute="_compute_display_name", store=False)

    def name_get(self):
        result = []
        for record in self:
            display_name = f"{record.name} / {record.description}" if record.description else record.name
            result.append((record.id, display_name))
        return result

    def _compute_display_name(self):
        for record in self:
            if record.description:
                record.display_name = f"{record.name} / {record.description}"
            else:
                record.display_name = record.name

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            domain = ['|', ('name', operator, name), ('description', operator, name)]
            records = self.search(domain + args, limit=limit)
        else:
            records = self.search(args, limit=limit)
        return records.name_get()