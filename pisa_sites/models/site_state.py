from odoo import fields, models

class SiteState(models.Model):
    _name = 'pisa.site.state'
    _description = 'Site State'
    _order = 'sequence'

    name = fields.Char(string="State Name", required=True)
    sequence = fields.Integer(string="Sequence", default=10)
    color = fields.Integer(string="Color")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'State name must be unique!')
    ] 