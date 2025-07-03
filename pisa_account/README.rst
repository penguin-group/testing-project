=============
PISA Accounting
=============

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-OPL--1-blue.png
    :target: https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps-licenses
    :alt: License: OPL-1
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/pisa_account
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

Customized features for PISA in the accounting application, including self-printed invoices and invoice approval workflows.

**Table of contents**

.. contents::
   :local:

Features
========

* **Self-printed Invoices**: Complete integration with Paraguay's self-printed invoice system
* **Invoice Approver Group**: Specialized permission group for invoice confirmation
* **Enhanced Bank Reconciliation**: Advanced bank reconciliation components
* **Secondary Currency Integration**: Full compatibility with secondary currency functionality
* **Custom Currency Rate Management**: Tools for managing and editing currency rates
* **Partner Enhancements**: Extended partner functionality for PISA requirements
* **Custom Reports**: PISA-specific invoice and payment reports

Overview
========

This module provides comprehensive accounting customizations specifically designed for PISA's business requirements. It integrates with Paraguay's localization features and extends Odoo's standard accounting functionality to meet PISA's unique operational needs.

Key Components
==============

**Self-printed Invoice System**

* Complete integration with l10n_py and l10n_py_selfprinted_invoice modules
* Automatic invoice formatting according to Paraguay regulations
* Custom invoice reports with PISA branding
* Sequential numbering and authorization management

**Invoice Approval Workflow**

* Specialized security group for invoice approvers
* Multi-level approval process configuration
* Audit trail for approval decisions
* Notification system for pending approvals

**Bank Reconciliation Enhancement**

* Advanced web components for bank reconciliation
* Improved user interface for reconciliation processes
* Automated matching algorithms
* Enhanced reporting for reconciliation status

**Currency Management**

* Integration with secondary_currency module
* Custom currency rate editing capabilities
* Rate variance reporting and alerts
* Historical rate tracking and analysis

Security Features
=================

**Invoice Approver Group**

The module introduces a specialized security group:

* **Invoice Approvers**: Users with permission to confirm and approve invoices
* Granular permissions for different invoice types
* Separation of duties for financial controls
* Audit logging for approval actions

**Access Controls**

* Restricted access to sensitive accounting functions
* Role-based permissions for different user types
* Enhanced security for financial data
* Compliance with internal control requirements

Models and Extensions
=====================

**Account Journal**

Enhanced journal functionality:

* PISA-specific journal configurations
* Integration with self-printed invoice settings
* Custom validation rules
* Enhanced reporting capabilities

**Account Move**

Extended invoice and journal entry features:

* Self-printed invoice support
* Approval workflow integration
* Secondary currency handling
* Custom field validations

**Account Payment**

Enhanced payment processing:

* Integration with bank reconciliation
* Secondary currency support
* Custom payment reports
* Approval workflow for large payments

**Partner (res.partner)**

Extended partner functionality:

* PISA-specific partner information
* Enhanced validation rules
* Custom partner reports
* Integration with Paraguay localization

Installation
============

To install this module, you need to:

#. Ensure dependencies are installed: ``base``, ``account_accountant``, ``l10n_py``, ``l10n_py_selfprinted_invoice``, ``secondary_currency``, ``account_custom_currency_rate``
#. Clone the repository
#. Add the module to your addons path
#. Update the module list
#. Install the module from Apps menu

Dependencies
============

This module depends on:

* ``base``: Core Odoo functionality
* ``account_accountant``: Advanced accounting features
* ``l10n_py``: Paraguay localization
* ``l10n_py_selfprinted_invoice``: Self-printed invoice functionality
* ``secondary_currency``: Dual currency support
* ``account_custom_currency_rate``: Currency rate management

Configuration
=============

After installation:

#. Configure invoice approval workflows
#. Set up self-printed invoice parameters
#. Configure secondary currency settings
#. Assign users to appropriate security groups
#. Customize reports and templates as needed

**Invoice Approval Setup**

#. Go to Settings > Users & Companies > Groups
#. Configure the "Invoice Approvers" group
#. Assign appropriate users to the group
#. Set up approval thresholds and rules

**Self-printed Invoice Configuration**

#. Configure journals for self-printed invoices
#. Set up invoice authorization parameters
#. Configure sequential numbering
#. Test invoice generation and printing

Usage
=====

**Creating Self-printed Invoices**

#. Create customer invoices as usual
#. Select journals configured for self-printed invoices
#. The system applies Paraguay formatting automatically
#. Print using PISA-customized templates

**Invoice Approval Process**

#. Invoices requiring approval are held in "To Approve" state
#. Designated approvers receive notifications
#. Approvers can review and approve/reject invoices
#. Audit trail tracks all approval decisions

**Bank Reconciliation**

#. Access enhanced reconciliation interface
#. Use improved matching algorithms
#. Process reconciliation with advanced tools
#. Generate reconciliation reports

**Currency Rate Management**

#. Edit currency rates when needed
#. View rate history and variance reports
#. Set up automatic rate updates
#. Monitor rate changes and impacts

Web Components
==============

The module includes specialized web components:

* **Bank Reconciliation**: Enhanced reconciliation interface
* **Currency Rate Editor**: User-friendly rate management
* **Invoice Approval**: Streamlined approval workflow
* **Multi-currency Display**: Clear dual currency presentation

Reporting
=========

**Custom Reports**

* PISA-branded invoice reports
* Payment vouchers with PISA formatting
* Bank reconciliation reports
* Currency variance reports

**Integration with Standard Reports**

* Enhanced trial balance with secondary currency
* Profit & loss with dual currency support
* Balance sheet with PISA formatting
* Cash flow reports with currency details

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