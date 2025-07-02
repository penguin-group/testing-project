=============
Fix OP-345
=============

.. |badge1| image:: https://img.shields.io/badge/maturity-Temporary-red.png
    :target: https://odoo-community.org/page/development-status
    :alt: Temporary
.. |badge2| image:: https://img.shields.io/badge/licence-OPL--1-blue.png
    :target: https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps-licenses
    :alt: License: OPL-1
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/temp_fix_op-345
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

Temporary module for reset journal entry 015-001-003045 and related payments to draft and fix secondary balance errors.

**Table of contents**

.. contents::
   :local:

Purpose
=======

This is a **temporary module** designed to fix a specific issue identified as OP-345. The module addresses secondary balance errors in a particular journal entry and its related payments.

.. warning::
   This is a temporary fix module. It should be removed after the issue has been resolved.

Issue Description
=================

**Ticket**: OP-345

**Problem**: Secondary balance errors in journal entry 015-001-003045 and related payments

**Solution**: Reset the affected journal entry and payments to draft state to allow manual correction of secondary balance discrepancies

Features
========

* **Targeted Fix**: Specifically addresses journal entry 015-001-003045
* **Payment Reset**: Resets related payments to draft state
* **Secondary Balance Correction**: Fixes secondary currency balance errors
* **Data Integrity**: Maintains data integrity while allowing corrections

Technical Details
=================

**Target Entry**: 015-001-003045

**Affected Components**:
* Journal entry and its lines
* Related payment records
* Secondary currency balances
* Account move reconciliation

**Operations Performed**:
* Reset journal entry to draft state
* Reset related payments to draft state
* Clear secondary currency inconsistencies
* Prepare for manual correction

Installation
============

.. warning::
   This module should only be installed temporarily to fix the specific issue.

To install this module:

#. Ensure the secondary_currency module is installed
#. Clone the repository
#. Add the module to your addons path
#. Update the module list
#. Install the module from Apps menu
#. Execute the fix operation
#. **Uninstall the module after use**

Dependencies
============

This module depends on:

* ``secondary_currency``: Required for secondary balance operations

Usage
=====

**Before Installation**

#. Back up your database
#. Verify the issue exists with journal entry 015-001-003045
#. Document current state for comparison

**Installation and Execution**

#. Install the module
#. The fix is applied automatically upon installation
#. Verify that the journal entry is reset to draft
#. Check that related payments are also in draft state

**After Fix Application**

#. Manually correct the secondary balance errors
#. Validate and post the journal entry
#. Reconcile related payments as needed
#. Verify that secondary balances are correct

**Cleanup**

#. Once the issue is resolved, uninstall this module
#. Remove the module from your addons path
#. Document the resolution for future reference

Verification Steps
==================

**Pre-fix Verification**

#. Check current state of journal entry 015-001-003045
#. Verify secondary balance errors exist
#. Document payment states

**Post-fix Verification**

#. Confirm journal entry is in draft state
#. Verify payments are reset to draft
#. Check that secondary balances can now be corrected
#. Ensure no data loss occurred

Manual Correction Process
=========================

After applying the fix:

#. Open journal entry 015-001-003045
#. Review and correct secondary currency amounts
#. Validate the entry to ensure balance
#. Post the corrected entry
#. Process related payments
#. Verify final balances are correct

Important Notes
===============

.. warning::
   **Temporary Module**: This module is designed for one-time use only.

.. caution::
   **Data Backup**: Always backup your database before applying this fix.

.. note::
   **Manual Steps Required**: The fix resets entries to draft but requires manual correction.

**Usage Guidelines**:

* Use only for the specific OP-345 issue
* Remove after successful fix application
* Document all manual corrections made
* Verify data integrity after completion

Bug Tracker
===========

This is a temporary fix module. For issues related to the underlying problem, refer to the main project's issue tracker at `GitHub Issues <https://github.com/penguin-group/pisa-addons/issues>`_.

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

This temporary module is maintained by Penguin Infrastructure.

.. image:: https://penguin.digital/logo.png
   :alt: Penguin Infrastructure
   :target: https://penguin.digital

Penguin Infrastructure is a software development company specialized in Odoo implementations. 