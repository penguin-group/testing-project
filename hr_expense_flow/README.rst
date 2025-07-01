==============
Expenses Flow
==============

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-OPL--1-blue.png
    :target: https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps-licenses
    :alt: License: OPL-1
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/hr_expense_flow
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

This module changes the behavior of the expenses to provide enhanced workflow options including company-paid, employee-paid, and petty cash payment methods.

**Table of contents**

.. contents::
   :local:

Features
========

* **Enhanced Payment Methods**: Three distinct payment workflows for different expense scenarios
* **Petty Cash Integration**: New payment method for petty cash expenses
* **Automated Vendor Bill Generation**: Automatic creation of vendor bills for expense processing
* **Clearing Journal Entries**: Automated clearing entries for proper accounting
* **Outstanding Balance Tracking**: Real-time tracking of outstanding expense balances
* **Department-based Petty Cash**: Petty cash accounts configured per department

Overview
========

This module revolutionizes expense management in Odoo by providing three distinct payment workflows, each designed for specific business scenarios. It automates the accounting processes behind expense management while providing transparency and control over expense flows.

Payment Methods
===============

**1. Paid by Company**

When an expense is paid by the company:

* **Vendor Bill Generation**: Creates a vendor bill (in draft) for each expense line using the configured expense journal
* **Reimbursement Account**: Credits the reimbursement account configured in expense settings
* **Clearing Entry**: Creates and confirms a clearing journal entry that:
  - Debits the reimbursement account
  - Credits the Expense Outstanding Account
  - Handles cases where expenses exceed available outstanding balance

**2. Paid by Employee**

When an expense is paid by the employee:

* **Vendor Bill Creation**: Generates a vendor bill (in draft) using the expense journal
* **Employee Reimbursement**: Credits the reimbursement account to the vendor
* **Clearing Process**: Creates a clearing entry that:
  - Debits the reimbursement account to the vendor
  - Credits the reimbursement account to the employee

**3. Petty Cash (New Option)**

New payment method for petty cash expenses:

* **Department Integration**: Petty cash accounts are configured at the department level
* **Account Selection**: Users can select from available petty cash accounts
* **Simplified Processing**: Direct posting to petty cash accounts
* **Department Controls**: Petty cash availability based on employee's department

Key Components
==============

**Outstanding Balance Management**

* Real-time calculation of outstanding expense balances
* Integration with expense outstanding accounts
* Automatic handling of over-limit situations
* Clear visibility of available balance

**Clearing Journal Entries**

* Automated generation of clearing entries
* Proper accounting treatment for different payment methods
* Configurable clearing journal settings
* Audit trail for all expense transactions

**Department-based Petty Cash**

* Petty cash account configuration per department
* Employee access based on department membership
* Flexible account selection for different expense types
* Control and monitoring of petty cash usage

Models and Extensions
=====================

**HR Expense (hr.expense)**

Enhanced expense functionality:

* **Outstanding Balance**: Computed field showing available outstanding balance
* **Payment Mode**: Extended with petty cash option
* **Petty Cash Account**: Selection field for petty cash accounts
* **Validation**: Enhanced constraints for petty cash usage

**HR Expense Sheet (hr.expense.sheet)**

Extended expense sheet processing:

* **Automated Bill Generation**: Creates vendor bills for expense lines
* **Clearing Entry Creation**: Generates appropriate clearing entries
* **Multi-method Support**: Handles different payment methods appropriately

**HR Department (hr.department)**

Department-level configuration:

* **Petty Cash Accounts**: Many2many field for department petty cash accounts
* **Access Control**: Determines available accounts for employees

**Company Settings (res.company)**

Additional configuration options:

* **Expense Outstanding Account**: Account for tracking outstanding expenses
* **Reimbursement Account**: Default reimbursement account
* **Clearing Journal**: Journal for clearing entries

Installation
============

To install this module, you need to:

#. Ensure the ``hr_expense`` module is installed
#. Clone the repository
#. Add the module to your addons path
#. Update the module list
#. Install the module from Apps menu

Dependencies
============

This module depends on:

* ``hr_expense``: Core expense functionality

Configuration
=============

After installation:

#. Configure expense settings in HR > Configuration > Settings
#. Set up reimbursement and outstanding accounts
#. Configure clearing journal
#. Set up petty cash accounts per department
#. Configure employee department assignments

**Company Configuration**

#. Go to Settings > Companies > Companies
#. Select your company and configure:
   - Expense Reimbursement Account
   - Expense Outstanding Account
   - Clearing Journal

**Department Setup**

#. Navigate to Employees > Configuration > Departments
#. For each department, configure available petty cash accounts
#. Ensure employees are properly assigned to departments

**Account Configuration**

#. Set up appropriate chart of accounts
#. Configure expense accounts and categories
#. Set up petty cash accounts as needed

Usage
=====

**Creating Company-Paid Expenses**

#. Create expense with payment mode "Paid by Company"
#. Submit expense for approval
#. Upon approval, system generates vendor bill and clearing entry
#. Outstanding balance is automatically managed

**Processing Employee-Paid Expenses**

#. Create expense with payment mode "Paid by Employee"
#. Submit for approval and processing
#. System creates vendor bill and clearing entry for reimbursement
#. Employee reimbursement is tracked automatically

**Using Petty Cash Expenses**

#. Create expense with payment mode "Petty Cash"
#. Select appropriate petty cash account from department options
#. Submit and process normally
#. System posts directly to selected petty cash account

Workflow Details
================

**Expense Submission**

1. Employee creates expense
2. Selects appropriate payment method
3. For petty cash, selects from available department accounts
4. Submits expense for approval

**Approval Process**

1. Manager reviews and approves expense
2. System validates all required information
3. Automatic processing begins upon approval

**Automatic Processing**

1. **Vendor Bill Generation**: Creates draft vendor bills
2. **Clearing Entry Creation**: Generates and posts clearing entries
3. **Balance Updates**: Updates outstanding balances
4. **Notifications**: Sends appropriate notifications

Advanced Features
=================

**Outstanding Balance Calculation**

* Real-time calculation based on posted journal entries
* Integration with expense outstanding account
* Automatic handling of insufficient balance scenarios
* Clear reporting of balance status

**Flexible Account Management**

* Department-based petty cash account configuration
* Multiple account options per department
* Easy account selection for users
* Administrative control over available accounts

**Audit and Compliance**

* Complete audit trail for all expense transactions
* Proper journal entry creation and posting
* Compliance with accounting standards
* Clear separation of different payment methods

Reporting
=========

* **Outstanding Balance Reports**: Track outstanding expense balances
* **Petty Cash Usage**: Monitor petty cash account usage by department
* **Expense Flow Analysis**: Analyze expense processing by payment method
* **Clearing Entry Reports**: Review all automated clearing entries

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/penguin-group/pisa-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

Authors
~~~~~~~

* Penguin Infrastructure S.A.

Maintainers
~~~~~~~~~~~

* José González <jose@penguin.digital>

This module is maintained by Penguin Infrastructure.

.. image:: https://penguin.digital/logo.png
   :alt: Penguin Infrastructure
   :target: https://penguin.digital

Penguin Infrastructure is a software development company specialized in Odoo implementations. 