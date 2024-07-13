from odoo import fields, models, api
from odoo.addons.base.models.ir_module import assert_log_admin_access


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    real_installed_version = fields.Char('Versión Instalada')
    module_real_installed_version_outdated = fields.Boolean(string='Módulo desactualizado', compute='_get_module_real_installed_version_outdated',
                                                            search='_search_module_real_installed_version_outdated')

    def _auto_init(self):
        res = super()._auto_init()
        for module in self.search([('state', '=', 'installed'), ('real_installed_version', 'in', (None, False, ''))]):
            module.write({'real_installed_version': module.installed_version})
        return res

    def _get_module_real_installed_version_outdated(self):
        module_version_strict_control = self.env['ir.config_parameter'].get_param('module_version_strict_control') != 'False'
        for this in self:
            module_real_installed_version_outdated = False
            if module_version_strict_control and this.real_installed_version and this.installed_version != this.real_installed_version:
                module_real_installed_version_outdated = True
            this.module_real_installed_version_outdated = module_real_installed_version_outdated

    def _search_module_real_installed_version_outdated(self, operator, value):
        if self.env['ir.config_parameter'].get_param('module_version_strict_control') == 'False':
            records = []
        else:
            records = self.search([]).filtered(lambda record: record.module_real_installed_version_outdated == value)
            records = records.ids
        return [('id', 'in', records)]

    def update_real_installed_version(self, operation):
        for this in self:
            modules_to_process = this
            while True:
                new_modules_to_process = this.env['ir.module.module.dependency'].search([
                    ('module_id', 'not in', modules_to_process.ids),
                    ('module_id.state', '=', 'installed'),
                    ('name', 'in', modules_to_process.mapped('name')),
                ]).module_id
                if new_modules_to_process:
                    modules_to_process |= new_modules_to_process
                else:
                    break
            for module_to_process in modules_to_process:
                if operation in ['install', 'update'] and module_to_process.state in ['installed']:
                    module_to_process.real_installed_version = module_to_process.installed_version
                if operation in ['uninstall'] and module_to_process.state in ['uninstalled']:
                    module_to_process.real_installed_version = False

    @assert_log_admin_access
    def button_immediate_install(self):
        res = super().button_immediate_install()
        self.update_real_installed_version(operation='install')
        return res

    @assert_log_admin_access
    def button_immediate_upgrade(self):
        res = super().button_immediate_upgrade()
        self.update_real_installed_version(operation='update')
        return res

    @assert_log_admin_access
    def button_immediate_uninstall(self):
        res = super().button_immediate_uninstall()
        self.update_real_installed_version(operation='uninstall')
        return res
