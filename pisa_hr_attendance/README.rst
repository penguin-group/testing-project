PISA HR Attendance
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

Module to handle specific attendance processes adapted to Penguin Infrastructure's business logic.

Features
========

* **File manipulation**: Parse CSV file exported from biometric clock containing attendance records.

Overview
========

As of now, this module aims to ease attendance tracking by allowing the upload of a CSV file exported from a biometric clock.
The main functionality -- the parse button -- cleans and restructure the data found on the uploaded CSV and then generates a new file
for the user to download.

Installation
============

To install this module, you need to:

#. Clone the pisa_addons repository if you haven't already. In case you do have the pisa_addons repo but you still don't see this module, make sure to ``git pull`` and get the latest version of pisa_addons.
#. Ensure dependencies are installed: ``base``, ``account``, ``web``, ``base_import``
#. Update the module list
#. Install the module from Apps menu

Dependencies
============

This module depends on:

* ``base``: Core Odoo functionality
* ``account``: Accounting module
* ``web``: The core of the Odoo Web Client
* ``base_import``: Odoo's native implementation for importing files


Usage
=====

**File manipulation: parse attendance records in CSV file**

#. Go to Attendances
#. Display tree view
#. Go to Actions button > Import records > Parse attendance file
#. Upload CSV exported from biometric clock
#. Parse it. A download is triggered.

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