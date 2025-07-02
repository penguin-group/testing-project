===================
Journal Entries Fix
===================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-OPL--1-blue.png
    :target: https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps-licenses
    :alt: License: OPL-1
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/pisa_account_fix
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

This module adds a server action in the account move to fix the invoice currency rate field in Odoo, enabling users to quickly and efficiently correct currency rate issues.

**Table of contents**

.. contents::
   :local:

Features
========

* **Currency Rate Fix**: Quick correction of invoice currency rate issues
* **Server Action Integration**: Easy access through server actions on account moves
* **Automated Cron Job**: Scheduled automatic fixing of currency rate issues
* **Bulk Processing**: Fix multiple journal entries simultaneously
* **Integration with PISA Account**: Seamless integration with PISA accounting modules
* **Audit Logging**: Track all currency rate corrections for compliance

Overview
========

This module provides essential functionality for correcting currency rate issues in invoice and journal entries. It introduces a server action that enables users to quickly identify and fix currency rate discrepancies that may occur due to system issues, data imports, or other operational scenarios.

The module is specifically designed to work with PISA's accounting infrastructure and provides both manual and automated approaches to currency rate correction.

Key Components
==============

**Server Action**

* **Quick Fix Action**: Server action available on account move forms
* **Bulk Operation**: Process multiple records simultaneously
* **User-friendly Interface**: Simple interface for currency rate corrections
* **Validation Logic**: Ensures corrections are appropriate and safe

**Automated Cron Job**

* **Scheduled Processing**: Automatic identification and fixing of rate issues
* **Configurable Schedule**: Flexible scheduling based on organizational needs
* **Error Handling**: Robust error handling for automated operations
* **Notification System**: Alerts for issues requiring manual intervention

**Currency Rate Validation**

* **Rate Verification**: Validate currency rates against system standards
* **Discrepancy Detection**: Automatically detect rate inconsistencies
* **Correction Logic**: Intelligent correction algorithms
* **Safety Checks**: Prevent inappropriate rate modifications

Problem Scenarios
=================

This module addresses common currency rate issues:

**Data Import Issues**

* **Import Discrepancies**: Correct rates from external system imports
* **Format Inconsistencies**: Handle different rate format standards
* **Historical Rate Issues**: Fix historical rate applications
* **Conversion Errors**: Correct calculation errors from imports

**System Integration Problems**

* **API Rate Issues**: Fix rates from external API integrations
* **Synchronization Problems**: Correct synchronization-related rate issues
* **Update Failures**: Handle failed automatic rate updates
* **Cache Issues**: Resolve cached rate inconsistencies

**Manual Entry Errors**

* **User Input Errors**: Correct manual rate entry mistakes
* **Timing Issues**: Fix rates applied at incorrect times
* **Currency Selection**: Correct incorrect currency selections
* **Rate Source Confusion**: Fix rates from incorrect sources

Installation
============

To install this module, you need to:

#. Ensure the ``pisa_account`` module is installed
#. Clone the repository
#. Add the module to your addons path
#. Update the module list
#. Install the module from Apps menu

Dependencies
============

This module depends on:

* ``pisa_account``: PISA accounting functionality

Configuration
=============

After installation:

#. Configure the automated cron job schedule
#. Set up notification preferences for automated fixes
#. Configure validation rules for currency rate corrections
#. Test the server action functionality
#. Set up user permissions for rate corrections

**Cron Job Configuration**

#. Navigate to Settings > Technical > Automation > Scheduled Actions
#. Locate the "Fix Invoice Currency Rate" cron job
#. Configure the execution schedule (default: daily)
#. Set up notification preferences
#. Configure error handling options

**User Permissions**

#. Configure user groups with rate correction permissions
#. Set up approval workflows if needed for significant corrections
#. Define audit and logging requirements
#. Test access controls with different user roles

Usage
=====

**Manual Currency Rate Fixing**

#. Open the account move requiring rate correction
#. Access the "Action" menu
#. Select "Fix Currency Rate" server action
#. Review the proposed corrections
#. Confirm and apply the fixes
#. Verify the corrected rates

**Bulk Processing**

#. Navigate to Accounting > Journal Entries
#. Select multiple entries requiring rate fixes
#. Access the "Action" menu
#. Select "Fix Currency Rate" for bulk processing
#. Review all proposed corrections
#. Apply fixes to selected entries

**Automated Processing**

#. The system automatically runs scheduled checks
#. Identifies entries with currency rate issues
#. Applies standard corrections automatically
#. Logs all automated corrections
#. Sends notifications for manual review items

Fix Logic and Algorithms
========================

**Rate Validation**

* **Source Verification**: Verify rates against authoritative sources
* **Range Checking**: Ensure rates are within reasonable ranges
* **Consistency Checks**: Validate rate consistency across related entries
* **Historical Comparison**: Compare against historical rate patterns

**Correction Algorithms**

* **Standard Correction**: Apply standard rate correction logic
* **Context-aware Fixes**: Consider transaction context for corrections
* **Weighted Averaging**: Use weighted averages for ambiguous cases
* **Business Rule Application**: Apply PISA-specific business rules

**Safety Mechanisms**

* **Backup Creation**: Create backups before applying corrections
* **Rollback Capability**: Ability to rollback incorrect fixes
* **Validation Steps**: Multiple validation steps before applying changes
* **User Confirmation**: Require user confirmation for significant changes

Integration Features
====================

**PISA Account Integration**

* **Secondary Currency**: Integration with secondary currency functionality
* **Custom Rate Management**: Works with custom currency rate features
* **Approval Workflows**: Integration with PISA approval workflows
* **Reporting Integration**: Corrections reflected in PISA reports

**System Integration**

* **Exchange Rate Services**: Integration with external rate services
* **Banking Systems**: Compatibility with banking system rates
* **ERP Integration**: Works with other ERP system integrations
* **API Compatibility**: Supports API-based rate corrections

**Audit and Compliance**

* **Change Logging**: Complete logging of all rate changes
* **User Tracking**: Track which users made corrections
* **Timestamp Recording**: Record exact timing of corrections
* **Reason Documentation**: Document reasons for corrections

Advanced Features
=================

**Intelligent Detection**

* **Pattern Recognition**: Identify rate issue patterns
* **Anomaly Detection**: Detect unusual rate variations
* **Predictive Analysis**: Predict potential rate issues
* **Machine Learning**: Learn from correction patterns

**Customization Options**

* **Custom Rules**: Define organization-specific correction rules
* **Threshold Configuration**: Configure detection thresholds
* **Notification Customization**: Customize notification preferences
* **Workflow Integration**: Integrate with custom workflows

**Performance Optimization**

* **Batch Processing**: Optimize for large-volume corrections
* **Memory Management**: Efficient memory usage for bulk operations
* **Database Optimization**: Optimized database queries
* **Caching Strategy**: Smart caching for performance improvement

Monitoring and Reporting
========================

**Fix Activity Reports**

* **Correction Summary**: Summary of all rate corrections
* **Error Analysis**: Analysis of common rate issues
* **Performance Metrics**: Track fix success rates and timing
* **User Activity**: Monitor user correction activities

**System Health Monitoring**

* **Rate Quality Metrics**: Monitor overall rate quality
* **Issue Frequency**: Track frequency of rate issues
* **Correction Effectiveness**: Measure correction effectiveness
* **System Performance**: Monitor system performance impact

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