======================
Completion Certificates
======================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-OPL--1-blue.png
    :target: https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps-licenses
    :alt: License: OPL-1
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/completion_certificates
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

Allows incremental vendor bills tied to purchase progress, ensuring transparent and structured billing throughout the service lifecycle.

**Table of contents**

.. contents::
   :local:

Features
========

* **Progress-based Billing**: Create vendor bills based on completion certificates
* **Purchase Order Integration**: Seamlessly integrates with purchase orders
* **Certificate Management**: Complete certificate lifecycle management
* **Approval Workflow**: Multi-level approval process for certificates
* **Automatic Invoice Generation**: Generates vendor bills automatically upon certificate confirmation
* **Line-by-line Tracking**: Track completion progress for each purchase order line
* **Price Adjustment**: Automatic price adjustment in vendor bills based on certificate data

Models
======

**Certificate (certificate)**

Main model representing a completion certificate with the following key fields:

* **Name**: Automatic sequence-generated certificate number
* **Reference**: Optional reference field
* **Partner**: Vendor (automatically populated from purchase order)
* **Purchase Order**: Related purchase order (required)
* **Date**: Certificate date
* **Total**: Computed total amount based on certificate lines
* **State**: Draft/Confirmed workflow states
* **Requester**: User who creates the certificate
* **Requester Manager**: Automatically computed from employee hierarchy
* **Vendor Bill**: Generated vendor bill linked to the certificate
* **Lines**: Certificate lines with detailed progress information

**Certificate Line (certificate.line)**

Detailed lines representing completion progress:

* **Description**: Line description
* **Quantity**: Original quantity from purchase order
* **Quantity Received**: Quantity completed in this certificate
* **Price Unit**: Unit price
* **Tax IDs**: Associated taxes
* **Price Subtotal**: Computed subtotal for the line

Installation
============

To install this module, you need to:

#. Ensure dependencies are installed: ``base``, ``purchase``, ``account_accountant``
#. Clone the repository
#. Add the module to your addons path
#. Update the module list
#. Install the module from Apps menu

Configuration
=============

After installation:

#. Go to Purchase > Configuration > Settings
#. Enable completion certificates for relevant purchase order types
#. Configure approval workflows if needed
#. Set up appropriate sequences for certificate numbering

Usage
=====

**Creating Completion Certificates**

#. Go to Purchase > Orders > Completion Certificates
#. Click "Create" to create a new certificate
#. Select a purchase order (must be in 'purchase' or 'done' state with certificates enabled)
#. The system automatically populates certificate lines based on purchase order lines
#. Adjust quantities received for each line as needed
#. Add any additional notes
#. Save the certificate

**Certificate Approval Process**

#. Submit the certificate for approval
#. The system routes it to the appropriate approvers based on the workflow
#. Once approved, confirm the certificate
#. The system automatically generates a vendor bill
#. Updates received quantities on purchase order lines

**Vendor Bill Generation**

When a certificate is confirmed:

#. A vendor bill is automatically created in draft state
#. Invoice lines correspond to certificate lines
#. Received quantities are updated on purchase order lines
#. Unit prices are adjusted if necessary to match certificate amounts

Workflow
========

1. **Certificate Creation**: User creates certificate linked to purchase order
2. **Line Configuration**: System populates lines from PO, user adjusts received quantities
3. **Submission**: Certificate submitted for approval
4. **Approval**: Goes through approval workflow
5. **Confirmation**: Certificate confirmed, vendor bill generated
6. **Invoice Processing**: Vendor bill can be reviewed and posted

Technical Details
=================

**Key Methods**

* ``action_confirm()``: Confirms certificate and generates vendor bill
* ``_onchange_purchase_order_id()``: Populates certificate lines from purchase order

**Constraints**

* Purchase orders must be in 'purchase' or 'done' state
* Purchase orders must have 'use_certificate' flag enabled
* Certificate lines cannot exceed original purchase order quantities

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/penguin-group/pisa-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

Authors
~~~~~~~

* Penguin Infrastructure

Maintainers
~~~~~~~~~~~

* José González <jose.gonzalez@penguin.digital>

This module is maintained by Penguin Infrastructure.

.. image:: https://penguin.digital/logo.png
   :alt: Penguin Infrastructure
   :target: https://penguin.digital

Penguin Infrastructure is a software development company specialized in Odoo implementations. 