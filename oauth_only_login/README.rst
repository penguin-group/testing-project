===============
OAuth Only Login
===============

Overview
========

This Odoo module customizes the login interface to hide traditional email/password login fields and only display OAuth provider login options. It's designed to enforce authentication through external OAuth providers while maintaining all of Odoo's standard authentication functionality.

Features
========

* **Hides email and password input fields** from the login form
* **Removes forgot password link** since passwords are managed by OAuth providers
* **Removes signup link** and redirects signup to OAuth providers
* **Keeps OAuth provider buttons visible** and prominently displayed
* **Maintains proper inheritance** of Odoo's authentication system
* **Responsive design** with improved styling for OAuth buttons

Dependencies
============

This module depends on the following Odoo modules:

* ``base`` - Core Odoo functionality
* ``web`` - Web interface components
* ``auth_oauth`` - OAuth authentication provider
* ``auth_signup`` - User signup functionality

Installation
============

1. Place this module in your ``pisa-addons`` directory
2. Update your Odoo apps list
3. Install the "OAuth Only Login" module from the Apps menu
4. Configure your OAuth providers in Settings > General Settings > Integrations

Configuration
=============

Setting up OAuth Providers
---------------------------

1. Go to **Settings > General Settings**
2. Enable **OAuth Authentication** under Integrations
3. Configure your OAuth providers (Google, Microsoft, etc.)
4. Test the OAuth authentication flow

Module Behavior
---------------

Once installed, the module will:

* Replace the standard login form with OAuth-only options
* Redirect signup attempts to OAuth providers
* Redirect password reset attempts to OAuth providers
* Maintain error/success message display functionality

Technical Details
=================

Template Inheritance
--------------------

The module uses Odoo's template inheritance system to modify the following templates:

* ``web.login`` - Main login form (replaced with OAuth-only version)
* ``auth_signup.login`` - Signup links removal
* ``auth_signup.signup`` - Signup form replacement
* ``auth_signup.reset_password`` - Password reset form replacement

CSS Customizations
------------------

The module includes custom CSS to:

* Hide any remaining password/email input fields
* Style OAuth provider buttons for better user experience
* Add hover effects and transitions
* Ensure responsive design

Priority Settings
-----------------

Template priorities are set to ensure this module's templates take precedence:

* Login form override: Priority 99
* Signup/reset overrides: Priority 100

Compatibility
=============

* **Odoo Version**: 18.0
* **License**: OPL-1
* **Author**: Penguin Infrastructure S.A.
* **Maintainer**: William Eckerleben

Troubleshooting
===============

Common Issues
-------------

1. **OAuth providers not showing**: Ensure ``auth_oauth`` module is installed and OAuth providers are properly configured
2. **Login form still visible**: Check module installation and template priorities
3. **CSS not applying**: Clear browser cache and restart Odoo server

Testing
-------

To test the module:

1. Install and configure at least one OAuth provider
2. Log out of Odoo
3. Navigate to the login page
4. Verify only OAuth provider buttons are visible
5. Test the OAuth authentication flow

Security Considerations
=======================

* This module enforces OAuth-only authentication, which can improve security by centralizing authentication through trusted providers
* Ensure your OAuth providers are properly configured with appropriate security settings
* Regular audit of OAuth provider configurations is recommended

Support
=======

For issues or questions regarding this module, please contact the Penguin Infrastructure S.A. development team at https://penguin.digital 