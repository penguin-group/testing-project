from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SiteTag(models.Model):
    _name = 'pisa.site.tag'
    _description = 'Site Tag'

    name = fields.Char(string="Tag Name", required=True)
    color_name = fields.Char(string="Color", default="blue")
    color = fields.Integer(compute="_compute_color", store=True)

    VALID_COLORS = [
        "red", "orange", "yellow", "sky blue", "purple", 
        "beige", "aquamarine", "blue", "pink", "green", "violet"
    ]

    @api.depends("color_name")
    def _compute_color(self):
        for record in self:
            color_lower = record.color_name.lower() if record.color_name else ''
            record.color = self.VALID_COLORS.index(color_lower) + 1 if color_lower in self.VALID_COLORS else 0

    @api.constrains('color_name')
    def _check_color(self):
        for record in self:
            if record.color_name and record.color_name.lower() not in self.VALID_COLORS:
                raise ValidationError(_(
                    "Invalid color. Please choose from: Red, Orange, Yellow, Sky Blue, "
                    "Purple, Beige, Aquamarine, Blue, Pink, Green, Violet"
                ))

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Tag name must be unique!')
    ] 