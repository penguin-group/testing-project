========================
Custom Currency Rate
========================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-OPL--1-blue.png
    :target: https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps-licenses
    :alt: License: OPL-1
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/account_custom_currency_rate
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

Custom Currency Rate management module that provides enhanced currency rate editing capabilities for invoice and journal entry processing.

**Table of contents**

.. contents::
   :local:
 
Features
========

* **Custom Currency Rate Editing**: Advanced interface for editing currency rates on invoices
* **Invoice Rate Management**: Ability to modify currency rates directly on account moves
* **User-friendly Wizard**: Intuitive wizard for currency rate adjustments
* **Multi-language Support**: Full Spanish language support included
* **Security Controls**: Proper access controls for currency rate modifications
* **Audit Trail**: Track changes to currency rates for compliance

Overview
========

This module enhances Odoo's standard currency rate functionality by providing users with the ability to edit and customize currency rates directly on invoices and journal entries. This is particularly useful for businesses that need to apply specific exchange rates for certain transactions or need to correct rates after initial entry.

Key Components
==============

**Invoice Rate Editor**

* Direct currency rate editing on account moves
* Real-time recalculation of amounts
* Validation of rate changes
* User-friendly interface for rate adjustments

**Currency Rate Wizard**

* Dedicated wizard for complex rate editing scenarios
* Batch rate updates for multiple transactions
* Preview of changes before application
* Confirmation dialogs for significant changes

**Security Framework**

* Role-based permissions for rate editing
* Audit logging for rate changes
* Approval workflows for significant rate modifications
* User access controls

Models and Extensions
=====================

**Account Move (account.move)**

Enhanced with currency rate editing capabilities:

* **Rate Editing Interface**: Direct rate modification on invoice forms
* **Recalculation Logic**: Automatic amount recalculation when rates change
* **Validation Rules**: Ensures rate changes are within acceptable parameters
* **History Tracking**: Maintains history of rate changes

**Currency Rate Wizard (invoice.edit.currency.rate)**

Specialized wizard for rate editing:

* **User-friendly Interface**: Simple form for rate modifications
* **Validation Logic**: Ensures data integrity during rate changes
* **Preview Functionality**: Shows impact of rate changes before applying
* **Confirmation Process**: Requires user confirmation for changes

Installation
============

To install this module, you need to:

#. Ensure dependencies are installed: ``base``, ``account``, ``web``
#. Clone the repository
#. Add the module to your addons path
#. Update the module list
#. Install the module from Apps menu

Dependencies
============

This module depends on:

* ``base``: Core Odoo functionality
* ``account``: Accounting module
* ``web``: Web interface components

Configuration
=============

After installation:

#. Configure user permissions for currency rate editing
#. Set up validation rules for rate changes (if needed)
#. Configure approval workflows for significant rate modifications
#. Test rate editing functionality with sample transactions

**User Permissions Setup**

#. Go to Settings > Users & Companies > Groups
#. Configure appropriate groups with rate editing permissions
#. Assign users to the correct groups based on their roles
#. Test access controls to ensure proper permissions

**Validation Configuration**

#. Configure acceptable rate variance thresholds
#. Set up approval requirements for large rate changes
#. Define notification rules for rate modifications
#. Test validation rules with various scenarios

Usage
=====

**Editing Currency Rates on Invoices**

#. Open an invoice or journal entry with foreign currency
#. Locate the currency rate field (enhanced interface)
#. Click the edit button or access the rate modification interface
#. Enter the new currency rate
#. Confirm the changes and review recalculated amounts

**Using the Currency Rate Wizard**

#. Access the wizard from the account move or through the menu
#. Select the transaction(s) requiring rate modification
#. Enter the new currency rate(s)
#. Preview the changes and their impact
#. Confirm and apply the modifications

**Bulk Rate Updates**

#. Select multiple transactions requiring rate updates
#. Access the bulk rate editing functionality
#. Apply rate changes to selected transactions
#. Review and confirm all modifications

Features in Detail
==================

**Real-time Recalculation**

* Automatic recalculation of amounts when rates change
* Preservation of original amounts for reference
* Clear display of rate change impacts
* Validation of calculated amounts

**User Interface Enhancements**

* Enhanced currency rate input fields
* Clear visual indicators for modified rates
* Intuitive navigation and controls
* Responsive design for mobile devices

**Data Integrity**

* Validation of rate changes to prevent errors
* Audit trail for all rate modifications
* Rollback capabilities for incorrect changes
* Data consistency checks

Security and Compliance
=======================

**Access Controls**

* Role-based permissions for rate editing
* Separation of duties for rate approval
* User activity logging
* Secure rate modification processes

**Audit Features**

* Complete audit trail for rate changes
* User identification for all modifications
* Timestamp tracking for rate changes
* Change reason documentation

**Compliance Support**

* Support for regulatory rate requirements
* Documentation of rate change justifications
* Approval workflows for compliance
* Reporting capabilities for audits

Advanced Configuration
======================

**Rate Validation Rules**

Configure validation rules to:

* Set acceptable rate variance thresholds
* Require approval for significant rate changes
* Prevent unauthorized rate modifications
* Ensure rate consistency across transactions

**Workflow Integration**

* Integration with approval workflows
* Notification systems for rate changes
* Escalation procedures for disputed rates
* Automated validation processes

Language Support
================

This module includes:

* **Spanish Language Pack**: Complete Spanish translation (``i18n/es.po``)
* **Multilingual Interface**: Support for multiple languages
* **Localization Support**: Adaptable to different regional requirements

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

* David Paez <david@penguin.digital>

Maintainers
~~~~~~~~~~~

This module is maintained by Penguin Infrastructure.

.. image:: https://penguin.digital/logo.png
   :alt: Penguin Infrastructure
   :target: https://penguin.digital

Penguin Infrastructure is a software development company specialized in Odoo implementations. 
