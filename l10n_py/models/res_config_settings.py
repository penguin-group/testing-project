from odoo import api, fields, models, release


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    inventory_book_base_report_bs = fields.Many2one(
        'account.report',
        string='Base Report for Balance Sheet',
        related='company_id.inventory_book_base_report_bs',
        help='Report structure to be used for the Balance Sheet in the Inventory Book report',
        readonly=False
    )
    inventory_book_base_report_is = fields.Many2one(
        'account.report',
        string='Base Report for Income Statement',
        related='company_id.inventory_book_base_report_is',
        help='Report structure to be used for the Income Statement in the Inventory Book report',
        readonly=False
    )
    show_inventory_book_base_report_bs_details = fields.Boolean(
        string='Show Account Details',
        related='company_id.show_inventory_book_base_report_bs_details',
        help='Detail the composition of the listed accounts: outstanding balances, inventory quantities, fixed asset listings, etc.',
        readonly=False
    )
