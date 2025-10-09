from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    miner_brand = fields.Char(string="Miner Brand", readonly=False)
    miner_model = fields.Char(string="Miner Model",  readonly=False)
    miner_hashrate_nominal = fields.Float(string="Hashrate Nominal (TH/s)", readonly=False)
    miner_theoretical_consumption = fields.Float(string="Theoretical Consumption (W)", readonly=False)
    miner_input_voltage_minimum = fields.Float(string="Input Voltage Minimum (V)", readonly=False)
    miner_input_voltage_maximum = fields.Float(string="Input Voltage Maximum (V)", readonly=False)
    miner_efficiency = fields.Float(string="Efficiency (J/TH)", readonly=False)
    miner_cooling_type = fields.Selection(
    selection=[
            ('fan', 'Fan Cooling'),
            ('hydro', 'Hydro Cooling'),
            ('immersion', 'Immersion Cooling'),
        ],
        string="Cooling Type",
    )

    is_miner_category = fields.Boolean(
        string="Is Miner Category",
        compute="_compute_is_miner_category",
        store=True
    )

    @api.depends('categ_id')
    def _compute_is_miner_category(self):
        miner_category = self.env.ref('pisa_inventory.product_category_miner', raise_if_not_found=False)
        for record in self:
            record.is_miner_category = record.categ_id == miner_category
