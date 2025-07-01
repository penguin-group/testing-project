=====================================
Secondary Currency Accounting Reports
=====================================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-OPL--1-blue.png
    :target: https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps-licenses
    :alt: License: OPL-1
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/secondary_currency_reports
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

View and create reports with secondary currency functionality, providing comprehensive dual-currency reporting capabilities.

**Table of contents**

.. contents::
   :local:

Features
========

* **Dual Currency Reporting**: Complete reporting functionality with secondary currency support
* **Multicurrency Revaluation**: Advanced revaluation reports for secondary currencies
* **Wizard-based Interface**: User-friendly wizards for report generation
* **Menu Integration**: Dedicated menu items for secondary currency reports
* **Data Export**: Multiple export formats for dual currency data
* **Integration with Accountant**: Full integration with accountant module features

Overview
========

This module extends Odoo's accounting reports to include comprehensive secondary currency functionality. It provides specialized reports that display amounts in both primary and secondary currencies, enabling better financial analysis and compliance for multi-currency operations.

Key Reports
===========

**Secondary Currency Multicurrency Revaluation Report**

Advanced revaluation reporting with secondary currency considerations:

* **Dual Currency Analysis**: Compare revaluation impacts in both currencies
* **Advanced Calculations**: Sophisticated revaluation algorithms
* **Period Comparisons**: Multi-period analysis capabilities
* **Export Functionality**: Multiple export formats supported

**Report Features**

* **Wizard Interface**: Interactive wizard for parameter selection
* **Flexible Filtering**: Comprehensive filtering options
* **Custom Date Ranges**: Configurable analysis periods
* **Data Export**: Excel, PDF, and other format support

Installation
============

To install this module, you need to:

#. Ensure dependencies are installed: ``accountant``, ``secondary_currency``
#. Clone the repository
#. Add the module to your addons path
#. Update the module list
#. Install the module from Apps menu

Dependencies
============

This module depends on:

* ``accountant``: Advanced accounting features
* ``secondary_currency``: Secondary currency functionality

Configuration
=============

After installation:

#. Configure secondary currency settings
#. Set up report parameters and defaults
#. Configure menu access permissions
#. Test report generation with sample data

Usage
=====

**Generating Reports**

#. Navigate to Accounting > Reporting > Secondary Currency Reports
#. Select the desired report type
#. Configure parameters using the wizard interface
#. Generate and review the report
#. Export in required format

**Multicurrency Revaluation**

#. Access the revaluation wizard
#. Set date ranges and currency parameters
#. Configure account filtering options
#. Generate comprehensive revaluation analysis
#. Export results for further analysis

Benefits
========

* **Enhanced Analysis**: Better financial analysis with dual currency visibility
* **Compliance Support**: Meet multi-currency reporting requirements
* **Decision Support**: Improved decision making with comprehensive currency data
* **Export Flexibility**: Multiple export options for different needs

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/penguin-group/pisa-addons/issues>`_.

Credits
=======

Authors
~~~~~~~

* Penguin Infrastructure

Contributors
~~~~~~~~~~~~

* William Eckerleben <william@penguin.digital>

Maintainers
~~~~~~~~~~~

This module is maintained by Penguin Infrastructure.

.. image:: https://penguin.digital/logo.png
   :alt: Penguin Infrastructure
   :target: https://penguin.digital

Penguin Infrastructure is a software development company specialized in Odoo implementations. 