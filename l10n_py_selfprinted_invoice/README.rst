===============================
Paraguay - Self-printed Invoice
===============================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-OPL--1-blue.png
    :target: https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps-licenses
    :alt: License: OPL-1
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/l10n_py_selfprinted_invoice
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

This module extends the Paraguay localization to support self-printed invoices according to Paraguay's tax regulations.

**Table of contents**

.. contents::
   :local:

Features
========

* **Self-printed Invoice Support**: Enables generation of self-printed invoices compliant with Paraguay regulations
* **Custom Invoice Reports**: Specialized invoice report templates for self-printed invoices
* **Invoice Layout**: Paraguay-specific invoice layout and formatting
* **Tax Compliance**: Ensures compliance with Paraguay's self-printed invoice requirements

Overview
========

Self-printed invoices are a specific type of invoice allowed under Paraguay's tax regulations for certain business scenarios. This module provides the necessary functionality to generate, format, and manage these invoices within Odoo.

Installation
============

To install this module, you need to:

#. Ensure the base Paraguay localization (l10n_py) is installed
#. Clone the repository
#. Add the module to your addons path
#. Update the module list
#. Install the module from Apps menu

Dependencies
============

This module depends on:

* ``base``: Core Odoo functionality
* ``account``: Accounting module

Configuration
=============

After installation:

#. Go to Accounting > Configuration > Journals
#. Configure journals that will use self-printed invoices
#. Set up the appropriate invoice report templates
#. Configure invoice numbering sequences if needed

Usage
=====

**Creating Self-printed Invoices**

#. Create a new customer invoice
#. Select a journal configured for self-printed invoices
#. Fill in the invoice details as usual
#. Validate the invoice
#. Print using the self-printed invoice report

**Report Generation**

The module provides specialized report templates that format invoices according to Paraguay's self-printed invoice requirements.

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

* Ivan Caceres <ivan@penguin.digital>

Maintainers
~~~~~~~~~~~

This module is maintained by Penguin Infrastructure.

.. image:: https://penguin.digital/logo.png
   :alt: Penguin Infrastructure
   :target: https://penguin.digital

Penguin Infrastructure is a software development company specialized in Odoo implementations. 