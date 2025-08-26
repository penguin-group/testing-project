Interfisa Localization (l10n)
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

Module responsible for generating an XLSX file needed by Banco Interfisa in order to perform payroll operations.

Features
========

* **Create payment report**: This module inherits the native payment report model found in Payroll. It changes the default file format for the report and allows the user to download the generated XLSX file.

Overview
========

The main purpose of this module is to overwrite the native behavior of Odoo's payment report functionality. This is needed in order to change the file format and build the file based on the structure needed by Banco Interfisa.


Installation
============

To install this module, you need to:

#. Clone the pisa_addons repository if you haven't already. In case you do have the pisa_addons repo but you still don't see this module, make sure to ``git pull`` and get the latest version of pisa_addons.
#. Ensure dependencies are installed: ``base``, ``account``, ``web``, ``hr_payroll``, ``l10n_hr_payroll_banks``
#. Update the module list
#. Install the module from the Apps menu

Dependencies
============

This module depends on:

* ``base``: Core Odoo functionality
* ``account``: Accounting module
* ``web``: The core of the Odoo Web Client
* ``hr_payroll``: Odoo's native payroll module (enterprise)
* ``l10n_hr_payroll_banks``: This module allows to add the bank to Payroll settings.


Usage
=====

**Create payment report**

#. Go to Payroll > Payslips > Batches
#. Choose a batch with a state of "Done"
#. Create payment report
#. The file is added to the payment_report field.

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