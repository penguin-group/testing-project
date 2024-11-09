from odoo import models, api

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def load_menus(self, debug):
        all_menus = super(IrUiMenu, self).load_menus(debug)

        in_paraguay = False

        if self.env.context.get('allowed_company_ids'):
                allowed_company_ids = self.env['res.company'].sudo().browse(self.env.context.get('allowed_company_ids'))
                in_paraguay = any([company.country_id.code == 'PY' for company in allowed_company_ids])
       
        # Example of filtering menus based on context or custom conditions
        # For example, hide certain menus based on a context value
        if in_paraguay:
            # paraguay_menu_ids = [menu.id for menu in all_menus.get('root', {}).get('children', []) if menu.get('name') == 'Special Menu']
            paraguay_menu_ids = [
                'book_registration_report_menu',
                'book_registration_menu',
                'invoice_authorization_menu',
                'report_res90_menu',
                'report_vat_purchase_wizard_menu',
                'report_vat_sale_wizard_menu',
            ]
            for menu_id in paraguay_menu_ids:
                all_menus['root']['children'].remove(menu_id)

        # # Example of modifying menu items - adding custom logic
        # for menu_id, menu in all_menus.items():
        #     # Add custom logic to modify menu attributes
        #     if menu.get('name') == 'Custom Menu':
        #         menu['sequence'] = 100  # Change sequence to appear at a specific order

        return all_menus
