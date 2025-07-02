============================
Paraguay - Accounting Reports
============================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png
    :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/l10n_py_reports
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

Specialized accounting reports for Paraguay localization, including multicurrency revaluation reports and compliance-focused financial reporting.

**Table of contents**

.. contents::
   :local:

Features
========

* **Multicurrency Revaluation Report**: Comprehensive currency revaluation reporting for Paraguay
* **Regulatory Compliance**: Reports designed to meet Paraguay's accounting and tax requirements
* **Wizard-based Interface**: User-friendly wizards for report generation and parameter selection
* **Integration with l10n_py**: Seamless integration with Paraguay localization features
* **Export Capabilities**: Multiple export formats for regulatory submissions

Overview
========

This module provides specialized accounting reports specifically designed for Paraguay's regulatory and business requirements. It extends the base Paraguay localization with additional reporting capabilities needed for compliance and financial management.

The module focuses on multicurrency revaluation reporting, which is particularly important for businesses operating in Paraguay's economic environment where currency fluctuations can significantly impact financial statements.

Key Reports
===========

**Multicurrency Revaluation Report**

Comprehensive report for currency revaluation analysis:

* **Currency Exposure Analysis**: Detailed analysis of foreign currency exposures
* **Revaluation Calculations**: Automatic calculation of unrealized gains/losses
* **Period Comparisons**: Compare revaluation impacts across different periods
* **Account-level Detail**: Detailed breakdown by account and currency
* **Regulatory Format**: Format compliant with Paraguay accounting standards

**Supporting Wizards**

* **Multicurrency Revaluation Wizard**: Interactive wizard for report generation
* **Parameter Selection**: Flexible parameter selection for different analysis needs
* **Date Range Selection**: Configurable date ranges for period analysis
* **Currency Selection**: Choose specific currencies for focused analysis

Models and Components
=====================

**Multicurrency Revaluation**

Core functionality for currency revaluation:

* **Automatic Calculations**: System automatically calculates revaluation impacts
* **Rate Integration**: Uses exchange rates from currency management system
* **Account Filtering**: Filter accounts based on currency exposure
* **Period Analysis**: Analyze revaluation impacts over different periods

**Report Data**

* **Structured Data Output**: Well-organized data for easy analysis
* **Multiple Formats**: Support for various output formats
* **Drill-down Capabilities**: Detailed analysis from summary to transaction level
* **Export Functionality**: Export to Excel, PDF, and other formats

Installation
============

To install this module, you need to:

#. Ensure the Paraguay localization (``l10n_py``) is installed
#. Clone the repository
#. Add the module to your addons path
#. Update the module list
#. Install the module from Apps menu

Dependencies
============

This module depends on:

* ``l10n_py``: Paraguay localization module

Configuration
=============

After installation:

#. Configure currency settings in the Paraguay localization
#. Set up exchange rate sources and update frequencies
#. Configure account classifications for currency exposure
#. Test report generation with sample data
#. Customize report formats as needed for your organization

**Currency Configuration**

#. Ensure all relevant currencies are properly configured
#. Set up automatic exchange rate updates
#. Configure default currency for reporting
#. Test currency conversion calculations

**Account Setup**

#. Classify accounts by currency exposure type
#. Set up account groups for reporting purposes
#. Configure account filters for different report types
#. Validate account classifications

Usage
=====

**Generating Multicurrency Revaluation Reports**

#. Navigate to Accounting > Reporting > Paraguay Reports
#. Select "Multicurrency Revaluation Report"
#. Configure report parameters:
   - Date range for analysis
   - Currencies to include
   - Account filters
   - Output format preferences
#. Generate and review the report
#. Export or print as needed

**Using the Revaluation Wizard**

#. Access the multicurrency revaluation wizard
#. Set report parameters:
   - Analysis period (from/to dates)
   - Base currency for calculations
   - Target currencies for analysis
   - Account categories to include
#. Preview report structure and data
#. Generate final report
#. Export in required format

Report Features
===============

**Comprehensive Analysis**

* **Currency Exposure**: Detailed analysis of foreign currency exposures
* **Unrealized Gains/Losses**: Calculation of unrealized currency gains and losses
* **Period Comparison**: Compare revaluation impacts across periods
* **Account Detail**: Account-by-account breakdown of currency impacts

**Regulatory Compliance**

* **Paraguay Standards**: Reports formatted according to Paraguay accounting standards
* **Tax Compliance**: Information formatted for tax reporting requirements
* **Audit Support**: Detailed documentation for audit purposes
* **Regulatory Submissions**: Export formats suitable for regulatory submissions

**Flexible Configuration**

* **Date Ranges**: Flexible date range selection for different analysis needs
* **Currency Selection**: Choose specific currencies for focused analysis
* **Account Filtering**: Filter accounts based on various criteria
* **Output Formats**: Multiple output formats for different uses

Technical Details
=================

**Data Sources**

* **Exchange Rates**: Uses official exchange rates from currency system
* **Account Balances**: Real-time account balance information
* **Historical Data**: Historical exchange rates for period comparisons
* **Transaction Details**: Detailed transaction information for drill-down

**Calculation Methods**

* **Standard Revaluation**: Standard multicurrency revaluation calculations
* **Paraguay-specific Rules**: Calculations aligned with Paraguay accounting rules
* **Tax Implications**: Consider tax implications of currency revaluations
* **Rounding Rules**: Proper rounding according to Paraguay standards

**Integration Points**

* **Currency Management**: Full integration with Odoo currency management
* **Account Structure**: Uses standard Odoo chart of accounts
* **Reporting Framework**: Built on Odoo's standard reporting framework
* **Export Systems**: Standard export capabilities with custom formats

Benefits for Paraguay Businesses
=================================

**Regulatory Compliance**

* **Standard Compliance**: Meet Paraguay accounting and reporting standards
* **Tax Preparation**: Simplified preparation of tax-related currency reports
* **Audit Readiness**: Comprehensive documentation for audit purposes
* **Regulatory Submissions**: Ready-to-submit reports for regulatory authorities

**Financial Management**

* **Currency Risk Management**: Better understanding of currency exposure risks
* **Financial Planning**: Improved financial planning with currency impact analysis
* **Performance Analysis**: Analyze business performance considering currency impacts
* **Decision Support**: Data-driven decision making regarding currency management

**Operational Efficiency**

* **Automated Calculations**: Reduce manual work in currency revaluation
* **Standardized Reporting**: Consistent reporting format across periods
* **Time Savings**: Significant time savings in report preparation
* **Error Reduction**: Reduced errors through automated calculations

Customization Options
=====================

**Report Formats**

* **Layout Customization**: Customize report layouts for organizational needs
* **Logo and Branding**: Add company logos and branding to reports
* **Additional Fields**: Include additional fields as needed
* **Format Modifications**: Modify formats for specific use cases

**Calculation Methods**

* **Custom Formulas**: Implement custom calculation formulas if needed
* **Rate Sources**: Configure alternative exchange rate sources
* **Rounding Rules**: Customize rounding rules for specific requirements
* **Period Definitions**: Define custom period structures for analysis

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/penguin-group/pisa-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

Authors
~~~~~~~

This module is part of the Odoo Paraguay localization suite.

Maintainers
~~~~~~~~~~~

This module is maintained by the Odoo Paraguay localization team.

.. image:: https://penguin.digital/logo.png
   :alt: Penguin Infrastructure
   :target: https://penguin.digital

Enhanced and maintained by Penguin Infrastructure, a software development company specialized in Odoo implementations. 