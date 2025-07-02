==================
Secondary Currency
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

Manages dual currencies for accurate transaction recording and reporting, facilitating international transactions and financial reporting.

**Table of contents**

.. contents::
   :local:

Features
========

* **Dual Currency Management**: Handle transactions in both primary and secondary currencies
* **Automatic Currency Conversion**: Real-time conversion between currencies
* **Enhanced Account Moves**: Extended invoice and journal entry functionality with dual currency support
* **Company-specific Settings**: Configure secondary currency settings per company
* **Advanced Reporting**: Generate reports showing amounts in both currencies
* **Web Interface Integration**: Enhanced UI components for currency management

Overview
========

This module provides comprehensive dual currency functionality for Odoo, enabling businesses to accurately record and report transactions in two currencies simultaneously. This is particularly useful for international businesses, companies operating in multiple countries, or organizations that need to maintain accounting records in both local and international currencies.

Key Benefits
============

* **International Compliance**: Meet reporting requirements for multiple jurisdictions
* **Real-time Conversion**: Automatic currency conversion using current exchange rates
* **Accurate Reporting**: Maintain precision in financial reporting across currencies
* **Enhanced Visibility**: Clear display of amounts in both currencies
* **Simplified Management**: Streamlined interface for dual currency operations

Technical Features
==================

**Model Extensions**

* **Account Move**: Enhanced with secondary currency fields and calculations
* **Company Settings**: Additional configuration options for secondary currency
* **Currency Conversion**: Advanced conversion logic with rate management

**User Interface**

* **Enhanced Forms**: Account move forms display both currencies
* **Custom Components**: Specialized web components for currency handling
* **Responsive Design**: Mobile-friendly currency input and display

**Reporting Integration**

* Full integration with account_reports module
* Dual currency amounts in all financial reports
* Customizable currency display formats

Installation
============

To install this module, you need to:

#. Ensure dependencies are installed: ``base``, ``account``, ``account_reports``
#. Clone the repository
#. Add the module to your addons path
#. Update the module list
#. Install the module from Apps menu

Dependencies
============

This module depends on:

* ``base``: Core Odoo functionality
* ``account``: Accounting module
* ``account_reports``: Enhanced reporting capabilities

Configuration
=============

After installation:

#. Go to Settings > General Settings > Secondary Currency
#. Configure the secondary currency for your company
#. Set up exchange rate sources and update frequencies
#. Configure currency conversion rules
#. Set default display preferences

**Company Configuration**

#. Navigate to Settings > Companies > Companies
#. Select your company
#. Configure secondary currency settings:
   - Secondary currency
   - Default conversion rate source
   - Rounding preferences
   - Display options

Usage
=====

**Creating Transactions with Secondary Currency**

#. Create a new invoice or journal entry
#. The system automatically displays amounts in both currencies
#. Primary currency amounts are entered as usual
#. Secondary currency amounts are calculated automatically
#. Manual adjustments can be made if needed

**Currency Rate Management**

#. Access currency rates via Accounting > Configuration > Currencies
#. Rates are updated automatically based on configuration
#. Manual rate updates are supported
#. Historical rates are maintained for accurate reporting

**Reporting**

#. Generate standard accounting reports
#. Reports automatically include both currency amounts
#. Filter and sort by either currency
#. Export reports with dual currency data

Web Components
==============

The module includes specialized web components:

* **Currency Input Fields**: Enhanced input fields for dual currency entry
* **Currency Display**: Formatted display of dual currency amounts
* **Rate Calculator**: Real-time currency conversion calculator
* **Historical Rate Viewer**: View historical exchange rates

Advanced Features
=================

**Rate Sources**

* Multiple exchange rate sources supported
* Automatic rate updates via scheduled jobs
* Manual rate override capabilities
* Rate validation and error handling

**Precision Management**

* Configurable rounding rules per currency
* Precision preservation in calculations
* Audit trail for rate changes
* Variance reporting for rate differences

**Multi-company Support**

* Different secondary currencies per company
* Company-specific rate sources
* Consolidated reporting across companies
* Inter-company transaction handling

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/penguin-group/pisa-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

Authors
~~~~~~~

* Penguin Infrastructure

Contributors
~~~~~~~~~~~~

* José González <jose@penguin.digital>

Maintainers
~~~~~~~~~~~

This module is maintained by Penguin Infrastructure.

.. image:: https://penguin.digital/logo.png
   :alt: Penguin Infrastructure
   :target: https://penguin.digital

Penguin Infrastructure is a software development company specialized in Odoo implementations. 