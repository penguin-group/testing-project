============
PISA Reports
============

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-OPL--1-blue.png
    :target: https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps-licenses
    :alt: License: OPL-1
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/pisa_reports
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

Customized reports for PISA with enhanced PDF export capabilities and secondary currency support.

**Table of contents**

.. contents::
   :local:

Features
========

* **Customized PISA Reports**: Specialized accounting reports designed for PISA's requirements
* **PDF Export Enhancement**: Custom PDF export templates with PISA branding
* **Secondary Currency Integration**: Full integration with secondary currency functionality
* **Custom Styling**: PISA-specific SCSS styling for PDF reports
* **Account Reports Extension**: Extends Odoo's standard account reports module

Overview
========

This module provides customized reporting functionality specifically designed for PISA's accounting needs. 
It extends Odoo's standard account reports module to include PISA-specific formatting, styling, and 
secondary currency support.

Features Details
================

**PDF Export Templates**

* Custom PDF export templates optimized for PISA's reporting requirements
* Professional layout and formatting
* PISA branding and styling integration
* Enhanced readability and presentation

**Secondary Currency Integration**

* Full compatibility with the secondary_currency module
* Dual currency reporting capabilities
* Automatic currency conversion and display
* Compliance with multi-currency reporting standards

**Custom Styling**

* PISA-specific SCSS styling for PDF reports
* Consistent branding across all reports
* Professional appearance and layout
* Optimized for printing and digital distribution

Installation
============

To install this module, you need to:

#. Ensure dependencies are installed: ``base``, ``account_reports``, ``secondary_currency``
#. Clone the repository
#. Add the module to your addons path
#. Update the module list
#. Install the module from Apps menu

Dependencies
============

This module depends on:

* ``base``: Core Odoo functionality
* ``account_reports``: Standard Odoo accounting reports
* ``secondary_currency``: Secondary currency functionality

Configuration
=============

After installation:

#. Go to Accounting > Reporting
#. Access the enhanced PISA reports
#. Configure secondary currency settings if needed
#. Customize PDF export templates as required

Usage
=====

**Generating Reports**

#. Navigate to Accounting > Reporting
#. Select the desired PISA report
#. Configure date ranges and filters
#. Choose export format (PDF recommended for enhanced styling)
#. Generate and download the report

**PDF Export**

#. Use the enhanced PDF export functionality
#. Reports will automatically apply PISA styling
#. Secondary currency amounts will be included if configured
#. Professional formatting will be applied automatically

**Secondary Currency Support**

If secondary currency is configured:

#. Reports will automatically display amounts in both currencies
#. Currency conversion rates will be applied
#. Both currencies will be clearly identified in the report

Technical Details
=================

**Assets**

The module includes custom SCSS assets for PDF export:

* ``pisa_reports/static/src/scss/pdf/pdf_pisa_report.scss``

**Data Files**

* ``data/pdf_export_templates.xml``: Custom PDF export templates
* ``views/account_report_views.xml``: Enhanced account report views

**Integration Points**

* Extends ``account.report`` model functionality
* Integrates with ``account_reports`` PDF export system
* Connects with ``secondary_currency`` for dual currency support

Customization
=============

**Styling Customization**

To customize the PISA styling:

#. Edit the SCSS file: ``static/src/scss/pdf/pdf_pisa_report.scss``
#. Modify colors, fonts, layout as needed
#. Update the module to apply changes

**Template Customization**

To customize PDF templates:

#. Edit ``data/pdf_export_templates.xml``
#. Modify template structure and content
#. Update the module to apply changes

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