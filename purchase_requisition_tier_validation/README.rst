=======================================
Purchase Requisition Tier Validation
=======================================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-OPL--1-blue.png
    :target: https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps-licenses
    :alt: License: OPL-1
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/purchase_requisition_tier_validation
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

Extends the functionality of Purchase Requisition (Purchase Agreements) to support a tier validation process, enabling multi-level approval workflows for purchase agreements.

**Table of contents**

.. contents::
   :local:

Features
========

* **Multi-tier Approval**: Comprehensive tier validation system for purchase requisitions
* **Configurable Workflows**: Flexible approval workflow configuration based on various criteria
* **Purchase Agreement Control**: Enhanced control over purchase agreement approval processes
* **Role-based Approvals**: Approval routing based on user roles and permissions
* **Audit Trail**: Complete audit trail for all approval decisions
* **Integration with Base Tier Validation**: Leverages the robust base tier validation framework

Overview
========

This module extends Odoo's Purchase Requisition (Purchase Agreement) functionality by adding a sophisticated tier validation system. This enables organizations to implement multi-level approval workflows for purchase agreements, ensuring proper oversight and control over procurement processes.

Purchase requisitions often involve significant financial commitments and vendor relationships, making approval workflows essential for proper governance and risk management.

Key Benefits
============

* **Enhanced Control**: Multi-level approval ensures proper oversight of purchase agreements
* **Risk Management**: Reduce financial and operational risks through structured approval processes
* **Compliance**: Meet organizational policies and regulatory requirements
* **Flexibility**: Configurable approval criteria based on amount, category, vendor, etc.
* **Transparency**: Clear audit trail for all approval decisions and processes

Tier Validation Framework
=========================

**Approval Criteria**

Configure approval tiers based on:

* **Agreement Amount**: Set different approval levels based on total agreement value
* **Product Categories**: Different approval flows for different product types
* **Vendor Types**: Special approval requirements for new or strategic vendors
* **Agreement Duration**: Extended agreements may require higher-level approval
* **Geographic Scope**: Multi-country agreements may need additional oversight

**Approval Routing**

* **Sequential Approval**: Each tier must approve before moving to the next level
* **Parallel Approval**: Multiple approvers at the same tier level
* **Conditional Routing**: Different paths based on agreement characteristics
* **Escalation Rules**: Automatic escalation for overdue approvals

**Approval States**

* **Draft**: Initial state, ready for submission
* **Under Validation**: In approval process
* **Validated**: All tiers approved, ready for confirmation
* **Rejected**: Rejected by one or more approvers
* **Cancelled**: Cancelled by requester or system

Models and Extensions
=====================

**Purchase Requisition (purchase.requisition)**

Enhanced with tier validation capabilities:

* **Tier Validation Integration**: Full integration with tier validation framework
* **Approval Status Display**: Clear indication of current approval status
* **Approver Information**: Display of required and completed approvals
* **Validation Controls**: Prevent unauthorized actions during approval process

**Tier Definition Integration**

* **Requisition-specific Rules**: Create validation rules specifically for purchase requisitions
* **Custom Criteria**: Define custom approval criteria for agreements
* **User Assignment**: Assign specific users or groups as approvers
* **Conditional Logic**: Complex approval logic based on multiple factors

Installation
============

To install this module, you need to:

#. Ensure dependencies are installed: ``purchase_requisition``, ``base_tier_validation``
#. Clone the repository
#. Add the module to your addons path
#. Update the module list
#. Install the module from Apps menu

Dependencies
============

This module depends on:

* ``purchase_requisition``: Core purchase requisition functionality
* ``base_tier_validation``: Tier validation framework

Configuration
=============

After installation:

#. Configure tier definitions for purchase requisitions
#. Set up approval criteria and thresholds
#. Assign approvers to different tiers
#. Configure notification and escalation rules
#. Test approval workflows with sample requisitions

**Tier Definition Setup**

#. Navigate to Settings > Technical > Tier Validation > Tier Definition
#. Create new tier definitions for purchase requisitions
#. Define approval criteria (amount thresholds, categories, etc.)
#. Set up approver assignments for each tier
#. Configure notification preferences

**Approval Workflow Configuration**

#. Define different approval paths for different scenarios
#. Set up escalation rules for delayed approvals
#. Configure notification templates and schedules
#. Test workflows with various requisition types

Usage
=====

**Creating Purchase Requisitions with Approval**

#. Create a new purchase requisition as usual
#. Fill in all required information (products, quantities, terms)
#. Submit the requisition for approval
#. System automatically determines required approval tiers
#. Notifications sent to appropriate approvers

**Approval Process**

#. Approvers receive notifications of pending requisitions
#. Review requisition details and supporting documentation
#. Approve or reject with optional comments
#. System automatically routes to next tier if approved
#. Final approval enables requisition confirmation

**Monitoring Approval Status**

#. View current approval status on requisition form
#. Track progress through approval tiers
#. Monitor pending approvals and bottlenecks
#. Generate reports on approval performance

Workflow Examples
=================

**Standard Purchase Agreement Workflow**

1. **Requisition Creation**: Procurement team creates purchase requisition
2. **Initial Review**: Department manager reviews and approves
3. **Budget Validation**: Finance team validates budget availability
4. **Executive Approval**: Senior management approves high-value agreements
5. **Confirmation**: Approved requisition can be confirmed and used

**Strategic Vendor Agreement**

1. **Strategic Assessment**: Special approval tier for strategic vendor evaluation
2. **Legal Review**: Legal team reviews contract terms and conditions
3. **Risk Assessment**: Risk management team evaluates vendor risks
4. **Executive Decision**: C-level approval for strategic partnerships
5. **Implementation**: Agreement activated for procurement use

**Category-specific Workflows**

Different approval flows based on product categories:

* **IT Equipment**: IT manager → Finance → General manager
* **Professional Services**: Department head → Finance → Legal → Executive
* **Raw Materials**: Production manager → Procurement → Finance
* **Capital Equipment**: Engineering → Finance → Operations → Executive

Advanced Features
=================

**Conditional Approval Logic**

* **Dynamic Routing**: Approval path changes based on requisition characteristics
* **Skip Logic**: Skip certain tiers based on predefined conditions
* **Parallel Processing**: Multiple approvers can work simultaneously
* **Exception Handling**: Special rules for urgent or emergency requisitions

**Integration Features**

* **Budget Integration**: Automatic budget validation during approval
* **Vendor Evaluation**: Integration with vendor assessment processes
* **Contract Management**: Link to contract approval workflows
* **Procurement Analytics**: Reporting on approval performance and bottlenecks

**Notification System**

* **Real-time Notifications**: Immediate notifications for pending approvals
* **Escalation Alerts**: Automatic escalation for overdue approvals
* **Status Updates**: Regular updates on approval progress
* **Customizable Templates**: Configurable notification templates

Benefits for Organizations
==========================

**Improved Governance**

* **Policy Compliance**: Ensure all agreements follow organizational policies
* **Risk Mitigation**: Multi-level review reduces procurement risks
* **Audit Readiness**: Complete audit trail for all approval decisions
* **Accountability**: Clear responsibility assignment for approval decisions

**Operational Efficiency**

* **Automated Routing**: Automatic approval routing reduces manual coordination
* **Parallel Processing**: Multiple approvers can work simultaneously
* **Exception Management**: Handle urgent requests with special procedures
* **Performance Monitoring**: Track and improve approval cycle times

**Financial Control**

* **Budget Oversight**: Ensure agreements align with budget approvals
* **Spend Control**: Multi-level approval for significant expenditures
* **Cost Optimization**: Review opportunities during approval process
* **Financial Risk Management**: Assess financial implications at each tier

Reporting and Analytics
=======================

**Approval Performance**

* **Cycle Time Analysis**: Track time spent at each approval tier
* **Bottleneck Identification**: Identify and address approval delays
* **Approver Performance**: Monitor individual approver response times
* **Workflow Efficiency**: Analyze and optimize approval processes

**Requisition Analytics**

* **Approval Rates**: Track approval vs. rejection rates by tier
* **Category Analysis**: Approval patterns by product category
* **Value Analysis**: Approval efficiency by agreement value
* **Vendor Analysis**: Approval patterns by vendor type

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

* José González <jose@penguin.digital>

This module is maintained by Penguin Infrastructure.

.. image:: https://penguin.digital/logo.png
   :alt: Penguin Infrastructure
   :target: https://penguin.digital

Penguin Infrastructure is a software development company specialized in Odoo implementations. 