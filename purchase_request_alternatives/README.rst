===============================
Purchase Request - Alternatives
===============================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-OPL--1-blue.png
    :target: https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps-licenses
    :alt: License: OPL-1
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/purchase_request_alternatives
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

Adds RFQ's alternatives compatibility to the purchase request module, enabling comprehensive vendor comparison and selection processes.

**Table of contents**

.. contents::
   :local:

Features
========

* **RFQ Alternatives Integration**: Links purchase requests with purchase requisition alternatives
* **Vendor Comparison**: Enables comparison of multiple vendor proposals for purchase requests
* **Enhanced Purchase Workflow**: Streamlined process from request to final purchase order selection
* **Alternative Management**: Comprehensive management of vendor alternatives and proposals
* **Decision Tracking**: Track vendor selection decisions and rationale

Overview
========

This module bridges the gap between purchase requests and purchase requisitions (alternatives/RFQs), creating a comprehensive procurement workflow that allows organizations to efficiently manage vendor comparisons and selection processes.

The integration enables users to convert purchase requests into RFQ processes where multiple vendors can submit proposals, compare alternatives, and select the best option based on various criteria.

Key Benefits
============

* **Competitive Procurement**: Enable competitive bidding processes for purchase requests
* **Vendor Evaluation**: Compare multiple vendor proposals systematically
* **Cost Optimization**: Select best value proposals through structured comparison
* **Process Transparency**: Clear audit trail from request to final vendor selection
* **Efficiency Gains**: Streamlined workflow reduces manual coordination

Workflow Integration
====================

**Standard Workflow Enhancement**

The module enhances the standard procurement workflow:

1. **Purchase Request Creation**: Users create purchase requests as usual
2. **RFQ Generation**: Convert approved requests to purchase requisitions
3. **Vendor Invitation**: Invite multiple vendors to submit proposals
4. **Alternative Comparison**: Compare vendor proposals side-by-side
5. **Vendor Selection**: Select winning proposal and generate purchase order
6. **Request Fulfillment**: Link final purchase order back to original request

**Process Benefits**

* **Request Traceability**: Maintain link between original request and final purchase
* **Vendor Competition**: Enable multiple vendors to compete for business
* **Structured Evaluation**: Systematic comparison of vendor proposals
* **Decision Documentation**: Record selection criteria and decisions

Models and Extensions
=====================

**Purchase Request Integration**

Enhanced purchase request functionality:

* **RFQ Relationship**: Direct relationship with purchase requisitions
* **Alternative Tracking**: Track all vendor alternatives for a request
* **Selection Status**: Monitor vendor selection progress
* **Final PO Link**: Connection to selected purchase order

**Purchase Requisition Enhancement**

Extended requisition capabilities:

* **Request Origin**: Link back to originating purchase request
* **Request Information**: Display original request details
* **Requester Visibility**: Show original requester information
* **Requirements Mapping**: Map request requirements to RFQ specifications

**Purchase Order Connection**

Enhanced purchase order tracking:

* **Request Origin**: Show originating purchase request
* **Alternative Context**: Display competing alternatives
* **Selection Rationale**: Document vendor selection reasons
* **Request Fulfillment**: Track request satisfaction status

Installation
============

To install this module, you need to:

#. Ensure dependencies are installed: ``purchase_requisition``, ``purchase_request``
#. Clone the repository
#. Add the module to your addons path
#. Update the module list
#. Install the module from Apps menu

Dependencies
============

This module depends on:

* ``purchase_requisition``: Purchase agreements and alternatives functionality
* ``purchase_request``: Purchase request management

Configuration
=============

After installation:

#. Configure purchase request to RFQ conversion rules
#. Set up vendor evaluation criteria
#. Configure approval workflows for vendor selection
#. Set up notification systems for stakeholders
#. Test the integrated workflow end-to-end

**Workflow Configuration**

#. Define criteria for when requests should go through RFQ process
#. Set up automatic RFQ generation rules
#. Configure vendor invitation processes
#. Define evaluation and selection criteria

**User Permissions**

#. Configure permissions for request creation
#. Set up RFQ management permissions
#. Define vendor selection approval rights
#. Configure visibility rules for different user roles

Usage
=====

**Converting Requests to RFQs**

#. Open an approved purchase request
#. Use the "Create RFQ" action to generate purchase requisition
#. System automatically populates RFQ with request details
#. Add vendor list and customize RFQ terms as needed
#. Send RFQ to vendors for proposal submission

**Managing Vendor Alternatives**

#. Vendors submit proposals through the requisition system
#. Review and compare all submitted alternatives
#. Evaluate proposals against defined criteria
#. Document evaluation results and selection rationale
#. Select winning proposal and generate purchase order

**Tracking Request Fulfillment**

#. Monitor progress from request through vendor selection
#. Track alternative evaluation status
#. Review final purchase order details
#. Confirm request fulfillment and close the process
#. Generate reports on procurement performance

Process Flow Examples
=====================

**Standard Competitive Procurement**

1. **Request Submission**: Employee submits purchase request for office equipment
2. **Approval Process**: Request goes through standard approval workflow
3. **RFQ Creation**: Approved request converted to RFQ for multiple vendors
4. **Vendor Proposals**: Three vendors submit proposals with different terms
5. **Evaluation**: Procurement team evaluates based on price, quality, delivery
6. **Selection**: Best value proposal selected and purchase order created
7. **Fulfillment**: Original request marked as fulfilled

**Service Procurement Process**

1. **Service Request**: Department requests consulting services
2. **Specification**: Detailed requirements documented in request
3. **RFQ Process**: RFQ sent to qualified service providers
4. **Proposal Review**: Multiple proposals received and evaluated
5. **Vendor Selection**: Provider selected based on capability and cost
6. **Contract Award**: Purchase order issued to selected vendor

Benefits for Procurement Teams
==============================

**Enhanced Vendor Management**

* Systematic vendor comparison processes
* Documentation of vendor selection decisions
* Performance tracking across procurement cycles
* Vendor relationship management

**Improved Cost Control**

* Competitive pricing through multiple proposals
* Structured evaluation of total cost of ownership
* Clear documentation of cost savings achieved
* Budget variance analysis and reporting

**Process Transparency**

* Clear audit trail from request to purchase order
* Documented evaluation criteria and decisions
* Stakeholder visibility into procurement process
* Compliance with procurement policies

**Efficiency Improvements**

* Automated workflow from request to RFQ
* Reduced manual coordination between teams
* Faster vendor evaluation and selection
* Streamlined communication with stakeholders

Reporting and Analytics
=======================

**Procurement Performance**

* Request-to-PO conversion metrics
* Vendor selection success rates
* Cost savings from competitive processes
* Cycle time analysis

**Vendor Analysis**

* Vendor participation rates in RFQs
* Win/loss ratios by vendor
* Vendor performance scoring
* Competitive analysis reports

**Process Efficiency**

* Request processing times
* RFQ response rates
* Evaluation cycle times
* Overall procurement efficiency metrics

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