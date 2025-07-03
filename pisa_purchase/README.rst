=============
PISA Purchase
=============

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-OPL--1-blue.png
    :target: https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps-licenses
    :alt: License: OPL-1
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/pisa_purchase
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

Customized features for PISA in the purchase application, integrating advanced procurement workflows and approval processes.

**Table of contents**

.. contents::
   :local:

Features
========

* **Purchase Requisition Integration**: Enhanced purchase requisition functionality
* **Tier Validation**: Multi-level approval workflows for purchase processes
* **Completion Certificates**: Integration with progress-based billing system
* **Project Integration**: Connection with project management for cost tracking
* **Purchase Request Enhancement**: Advanced purchase request workflows
* **Custom Views**: PISA-specific purchase and request views

Overview
========

This module extends Odoo's standard purchase functionality to meet PISA's specific procurement requirements. It integrates multiple advanced modules to create a comprehensive procurement management system with approval workflows, progress tracking, and project integration.

Key Integrations
================

**Purchase Requisition System**

* Advanced requisition management
* Multi-vendor comparison processes
* Automated RFQ generation
* Supplier evaluation and selection

**Tier Validation Framework**

* Multi-level approval workflows
* Configurable approval criteria
* Role-based approval assignments
* Audit trail for all approvals

**Completion Certificates**

* Progress-based billing integration
* Milestone tracking and verification
* Automated invoice generation
* Service completion validation

**Project Management**

* Cost tracking by project
* Budget monitoring and controls
* Resource allocation tracking
* Project-specific procurement rules

**Purchase Request System**

* Centralized request management
* Approval workflow integration
* Budget validation
* Automated PO generation

Models and Extensions
=====================

**Purchase Order (purchase.order)**

Enhanced purchase order functionality:

* Integration with completion certificates
* Project assignment and tracking
* Multi-level approval workflows
* Custom validation rules

**Purchase Request (purchase.request)**

Extended request functionality:

* PISA-specific workflow processes
* Enhanced approval mechanisms
* Project integration
* Budget controls

Installation
============

To install this module, you need to:

#. Ensure dependencies are installed: ``base``, ``purchase_requisition``, ``purchase_tier_validation``, ``purchase_request_tier_validation``, ``completion_certificates``, ``project``, ``account``
#. Clone the repository
#. Add the module to your addons path
#. Update the module list
#. Install the module from Apps menu

Dependencies
============

This module depends on:

* ``base``: Core Odoo functionality
* ``purchase_requisition``: Purchase agreements and requisitions
* ``purchase_tier_validation``: Tier validation for purchases
* ``purchase_request_tier_validation``: Tier validation for purchase requests
* ``completion_certificates``: Progress-based billing
* ``project``: Project management
* ``account``: Accounting integration

Configuration
=============

After installation:

#. Configure tier validation rules for purchases
#. Set up approval workflows for different purchase types
#. Configure completion certificate parameters
#. Set up project integration settings
#. Configure purchase request workflows

**Tier Validation Setup**

#. Go to Settings > Technical > Tier Validation > Tier Definition
#. Create validation rules for purchase orders
#. Define approval criteria (amount, category, etc.)
#. Assign approvers for each tier

**Completion Certificate Configuration**

#. Enable completion certificates for relevant purchase types
#. Configure milestone definitions
#. Set up billing schedules
#. Define validation criteria

Usage
=====

**Purchase Order Workflow**

#. Create purchase orders as usual
#. Orders automatically enter approval workflow
#. Approvers receive notifications
#. Once approved, orders can be confirmed
#. Progress tracking via completion certificates

**Purchase Request Process**

#. Users create purchase requests
#. Requests go through approval workflow
#. Approved requests generate purchase orders
#. Integration with budget controls
#. Project assignment and tracking

**Completion Certificate Management**

#. Create certificates for service milestones
#. Validate completion progress
#. Generate invoices based on progress
#. Track project completion status

**Project Integration**

#. Assign purchases to specific projects
#. Track costs by project phase
#. Monitor budget vs actual spending
#. Generate project cost reports

Workflows
=========

**Standard Purchase Workflow**

1. **Request Creation**: Users create purchase requests
2. **Request Approval**: Multi-tier approval process
3. **RFQ Generation**: Approved requests generate RFQs
4. **Vendor Selection**: Compare and select vendors
5. **PO Confirmation**: Final approval and confirmation
6. **Progress Tracking**: Monitor delivery and completion

**Service Purchase Workflow**

1. **Service Request**: Create request for services
2. **Approval Process**: Multi-level approval
3. **PO Creation**: Generate purchase order
4. **Certificate Creation**: Create completion certificates
5. **Progress Validation**: Validate service completion
6. **Invoice Generation**: Generate invoices based on progress

Views and Interface
===================

**Custom Purchase Views**

* Enhanced purchase order forms
* Integrated approval status display
* Project information sections
* Certificate tracking panels

**Purchase Request Views**

* Streamlined request creation forms
* Approval workflow indicators
* Budget validation displays
* Project assignment interfaces

**Reporting Integration**

* Purchase analysis by project
* Approval workflow reports
* Completion certificate status
* Budget vs actual reports

Technical Details
=================

**Key Methods**

* Purchase order validation enhancements
* Approval workflow triggers
* Certificate integration logic
* Project cost tracking calculations

**Data Flow**

* Request → Approval → PO → Delivery → Certificate → Invoice
* Integrated validation at each step
* Automatic status updates
* Audit trail maintenance

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