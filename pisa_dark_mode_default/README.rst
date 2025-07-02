========================
PISA Dark Mode Default
========================

Overview
========

This module automatically sets dark mode as the default theme for all users in Odoo, implementing the user story requirements for enhanced user experience.

User Story Implemented
======================

**As a system user**, I want dark mode to be the default theme and English the primary language so that I have a consistent and comfortable user experience upon first access, with the option to switch to light mode or Spanish if desired.

Features
========

✅ Acceptance Criteria Met
--------------------------

1. **Dark mode is the default UI theme on initial access for all users**
2. **English is set as the default language for the interface** (handled by Odoo core)
3. **Users retain the ability to manually switch to light mode or Spanish**
4. **Preferences must persist across sessions for logged-in users**

Technical Implementation
------------------------

* **Cookie-based approach**: Uses Odoo's native ``color_scheme`` cookie mechanism
* **Non-intrusive**: Respects existing user preferences
* **Inheritance-based**: Extends ``ir.http`` model following Odoo best practices
* **Future-proof**: Compatible with Odoo's existing dark mode infrastructure

How It Works
============

1. **Context Detection**: The ``ir.http`` model detects when no ``color_scheme`` cookie exists and provides a ``default_dark_mode`` context variable
2. **Template Override**: A template inheritance modifies the webclient to load dark assets when either the cookie is 'dark' OR no preference exists
3. **Cookie Setting**: For future sessions, the module sets the ``color_scheme`` cookie to 'dark'
4. **User Choice**: If users manually switch themes, their preference is stored and respected
5. **Persistence**: The cookie has a 1-year expiration, ensuring long-term persistence

Installation
============

1. **Copy the module** to your ``pisa-addons`` directory
2. **Update the addons list**::

   ./odoo-bin -u all -d your_database

3. **Install the module**:
   
   * Go to Apps
   * Search for "PISA Dark Mode Default"
   * Click Install

File Structure
==============

::

    pisa_dark_mode_default/
    ├── __init__.py                 # Module initialization
    ├── __manifest__.py             # Module configuration
    ├── README.rst                  # This documentation
    ├── models/
    │   ├── __init__.py             # Models initialization
    │   └── ir_http.py              # Backend logic for cookie management
    └── views/
        └── webclient_templates.xml # Template inheritance for dark mode logic

Code Architecture
=================

Key Components
--------------

1. **ir_http.py**: Inherits from ``ir.http`` and overrides:
   
   * ``webclient_rendering_context()``: Provides ``default_dark_mode`` context variable

2. **webclient_templates.xml**: Template inheritance that modifies:
   
   * Dark mode detection logic to include default behavior
   * Asset loading conditions for immediate dark mode application

3. **Cookie Management**:
   
   * **Name**: ``color_scheme``
   * **Value**: ``dark``
   * **Duration**: 1 year
   * **Security**: SameSite=Lax, httponly=False (allows JS theme switching)

Integration Points
------------------

* **Odoo Core**: Uses existing dark mode infrastructure
* **Theme Switching**: Compatible with native theme toggle functionality
* **Enterprise Edition**: Works alongside web_enterprise module

Testing
=======

Manual Testing Steps
--------------------

1. **Clear browser cookies** for your Odoo instance
2. **Access Odoo** in a fresh browser session
3. **Verify**: Interface should load in dark mode by default
4. **Test switching**: Use any theme toggle to switch to light mode
5. **Refresh page**: Verify light mode preference persists
6. **New incognito window**: Should default to dark mode again

Expected Behavior
-----------------

* ✅ New users see dark mode immediately
* ✅ Existing user preferences are preserved
* ✅ Theme switching works normally
* ✅ Preferences persist across sessions
* ✅ No impact on system performance

Compatibility
=============

* **Odoo Version**: 17.0+
* **Dependencies**: ``base``, ``web``
* **Enterprise**: Compatible with web_enterprise
* **Browsers**: All modern browsers supporting cookies

Technical Notes
===============

Cookie Lifecycle
-----------------

.. code-block:: python

    # Set when no preference exists
    request.future_response.set_cookie(
        'color_scheme', 
        'dark',
        max_age=60 * 60 * 24 * 365,  # 1 year
        httponly=False,               # Allow JS access
        samesite='Lax'               # Security
    )

Asset Loading Logic
-------------------

.. code-block:: xml

    <!-- Original logic -->
    <t t-if="request.cookies.get('color_scheme') == 'dark'">
        <t t-call-assets="web.assets_web_dark" media="screen"/>
    </t>

    <!-- Our enhanced logic -->
    <t t-if="request.cookies.get('color_scheme') == 'dark' or default_dark_mode">
        <t t-call-assets="web.assets_web_dark" media="screen"/>
    </t>

Troubleshooting
===============

**Issue: Dark mode not applying**
    **Solution**: Clear browser cookies and refresh

**Issue: Can't switch back to light mode**
    **Solution**: Check if theme toggle functionality is available in your Odoo version

**Issue: Module not loading**
    **Solution**: Verify module is in correct addons path and dependencies are met

Future Enhancements
===================

Potential improvements for future versions:

1. **User-level settings**: Database field for per-user default theme
2. **Company-level defaults**: Different defaults per company
3. **Time-based switching**: Automatic dark/light mode based on time
4. **Custom theme options**: Additional theme variants

Support
=======

For issues related to this module:

1. **Check logs**: Review Odoo server logs for errors
2. **Verify installation**: Ensure module is properly installed and activated
3. **Test environment**: Try in a clean Odoo instance
4. **Contact**: Reach out to the PISA development team

License
=======

LGPL-3 - See LICENSE file for details 