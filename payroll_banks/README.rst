Payroll Banks
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

Module responsible for including settings related to banks used for payroll operations.

Features
========

* **Set bank from payroll settings**: From a list of banks, choose the one to be used in the payroll module.

Overview
========

The main purpose of this module is to manage which are the banks available for payroll operations. The model responsible for adding new banks are to be inherited in other modules and append banks to the dropdown list found in Payroll settings.

Installation
============

To install this module, you need to:

#. Clone the pisa_addons repository if you haven't already. In case you do have the pisa_addons repo but you still don't see this module, make sure to ``git pull`` and get the latest version of pisa_addons.
#. Ensure dependencies are installed: ``base``, ``account``, ``web``, ``hr_payroll``
#. Update the module list
#. Install the module from the Apps menu

Dependencies
============

This module depends on:

* ``base``: Core Odoo functionality
* ``account``: Accounting module
* ``web``: The core of the Odoo Web Client
* ``hr_payroll``: Odoo's native payroll module (enterprise)


Usage
=====

**Set bank from payroll settings**

#. Go to Settings > Payroll
#. You should see a dropdown "Bank used for employees salary"
#. Choose the corresponding bank, if any
#. Save

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