from odoo import models, fields, api, _
import json
import base64
import io
from datetime import date
from odoo.exceptions import UserError
from ..utils.ips_report_data import IPSReportData


class HrReportsIPS(models.Model):
    _name = 'hr.reports.ips'
    _inherit = ['mail.thread']
    _description = 'IPS Reports'   

    name = fields.Char(
        string="Name",
        compute='_compute_name',
        store=True,
        readonly=True
    )
    year = fields.Selection(
        [(str(y), str(y)) for y in range(2000, fields.Date.today().year + 1)],
        string='Year',
        required=True,
        default=lambda self: str(fields.Date.today().year)
    )
    month = fields.Selection(
        [(str(m), str(m)) for m in range(1, 13)],
        string="Month",
        required=True,
        default=lambda self: str(fields.Date.today().month)
    )
    data = fields.Json("Data")
    txt_output = fields.Binary(string='File', )
    txt_filename = fields.Char(string='File Name', compute="_compute_filename", store=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company)



    @api.depends('year')
    def _compute_name(self):
        for record in self:
            if record.year and record.month:
                record.name = record.year + " - " + record.month
            else:
                record.name = "/"
    
    @api.depends('name')
    def _compute_filename(self):
        for record in self:
            record.txt_filename = f"{record.name}.txt" if record.name else False
    
    def action_generate(self):
        self.ensure_one()
        
        self._populate_data()
        data = self.data or []

        output = io.StringIO()
        for row in data:
            output.write("\t".join(map(str, row)) + "\n")

        output.seek(0)

        file_content = output.getvalue().encode("utf-8")
        
        self.write({
            'txt_output': base64.b64encode(file_content),
        })

    def _populate_data(self):
        """
        This method generates a list of items.
        """

        self.data = [] # default
        report_data = IPSReportData(self.env, int(self.year), int(self.month))
        self.data = report_data.salaries

