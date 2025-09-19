Odoo 19 Features Backport
==================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-OPL--1-blue.png
    :target: https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps-licenses
    :alt: License: OPL-1
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/secondary_currency
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|


Features
========

* **Forward Compatibility**: Safely introduces Odoo 19 features to Odoo 18 environments
* **Bulk User Creation**: Add a server action to create users in bulk from selected employees

Overview
========

The Odoo 19 Features Backport module addresses the need for accessing newer Odoo functionality without upgrading your entire system. This module focuses on HR-related improvements, specifically enabling administrators to efficiently create user accounts for multiple employees simultaneously.

Key Benefits:

- **Time Saving**: Create multiple user accounts in one action instead of manually creating them one by one
- **Consistency**: Ensures uniform user creation process across your organization  
- **Integration**: Seamlessly works with existing HR employee records
- **Future-Ready**: Prepares your system for eventual Odoo 19 migration

Installation
============

1. **Download the Module**:
   
   Download or clone this module to your Odoo addons directory::

    git clone <repository-url> /path/to/odoo/addons/odoo19_backport

2. **Update Apps List**:
   
   Restart your Odoo server and update the apps list:
   
   - Go to **Apps** menu
   - Click **Update Apps List**
   - Search for "Odoo 19 Features Backport"

3. **Install the Module**:
   
   - Locate the module in the Apps list
   - Click **Activate**

4. **Verify Installation**:
   
   Check that the module appears in your installed modules list under **Apps > Installed Apps**.

Dependencies
============

This module requires the following Odoo modules:

Core Dependencies:
~~~~~~~~~~~~~~~~~~

* **base**: Core Odoo functionality (automatically installed)
* **hr**: Human Resources module for employee management

System Requirements:
~~~~~~~~~~~~~~~~~~~~

* **Odoo Version**: 18.0 or higher
* **Python Version**: 3.8 or higher  
* **Database**: PostgreSQL 12 or higher


Usage
=====

Bulk User Creation from Employees
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Navigate to Employees**:
   
   Go to **Employees**

2. **Select Multiple Employees**:
   
   - Use the list view to see all employees
   - Select the employees you want to create users for using the checkboxes
   - You can select multiple employees at once

3. **Execute Server Action**:
   
   - Click on the **Action** dropdown menu (⚙️ gear icon)
   - Select **Create User**
   - The system will process the selected employees

4. **Review Created Users**:
   
   - Navigate to **Settings > Users & Companies > Users**
   - Verify that new user accounts have been created
   - Each user will be linked to their corresponding employee record


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/penguin-group/pisa-addons/issues>`.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

Authors
~~~~~~~

* Penguin Infrastructure

Contributors
~~~~~~~~~~~~

* David Páez <david.jacquet@penguin.digital>

Maintainers
~~~~~~~~~~~

This module is maintained by Penguin Infrastructure.

.. image:: https://penguin.digital/logo.png
   :alt: Penguin Infrastructure
   :target: https://penguin.digital

Penguin Infrastructure is a software development company specialized in Odoo implementations.