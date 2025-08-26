from . import models

def _post_init_hook(env):

    admin_user = env.ref('base.user_admin', raise_if_not_found=False)
    if admin_user:
        config_settings = env['res.config.settings'].create({
            'group_stock_production_lot': True,
        })
        config_settings.execute()