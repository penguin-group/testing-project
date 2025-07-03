==========================
Base Tier Validation HR
==========================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-OPL--1-blue.png
    :target: https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps-licenses
    :alt: License: OPL-1
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/base_tier_validation_hr
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

This module allows the Employee Role to be used in the Tier Definition model, extending the base tier validation framework with HR-specific capabilities.

**Table of contents**

.. contents::
   :local:

Features
========

* **Employee Role Integration**: Enables employee roles in tier validation definitions
* **HR-based Approval Workflows**: Create approval workflows based on employee roles and hierarchy
* **Enhanced Tier Definitions**: Extended tier definition model with HR employee role support
* **Role-based Validations**: Configure validation rules based on employee roles and positions
* **Organizational Hierarchy**: Leverage employee hierarchy for approval workflows

Overview
========

This module extends the base tier validation framework by integrating HR employee roles into the tier definition system. This allows organizations to create sophisticated approval workflows that are based on employee roles, positions, and organizational hierarchy rather than just user groups.

This integration enables more natural and flexible approval processes that align with organizational structures and reporting relationships.

Key Benefits
============

* **Organizational Alignment**: Approval workflows that match organizational structure
* **Role-based Logic**: Use employee roles instead of just user groups for approvals
* **Hierarchy Integration**: Leverage manager-employee relationships in approval flows
* **HR-centric Workflows**: Design workflows that make sense from an HR perspective
* **Flexible Configuration**: Combine employee roles with other tier validation criteria

Integration Components
======================

**Tier Definition Enhancement**

The module extends the tier definition model to include:

* **Employee Role Selection**: Ability to select employee roles as approval criteria
* **Department Integration**: Use department information in approval logic
* **Manager Hierarchy**: Leverage reporting relationships for approval routing
* **Position-based Rules**: Create rules based on employee positions

**HR Module Integration**

Seamless integration with Odoo's HR module:

* **Employee Model**: Direct integration with employee records
* **Role Management**: Use existing HR role definitions
* **Department Structure**: Leverage department hierarchy
* **Reporting Lines**: Use manager-employee relationships

Model Extensions
================

**Tier Definition (tier.definition)**

Enhanced with HR capabilities:

* **Employee Role Fields**: New fields for employee role selection
* **HR-based Criteria**: Additional criteria based on HR information
* **Department Filters**: Filter approvers by department
* **Position Requirements**: Set position-based approval requirements

**Integration Points**

* **Employee Records**: Direct link to hr.employee model
* **Department Structure**: Integration with hr.department
* **Job Positions**: Connection to hr.job for position-based rules
* **User-Employee Link**: Automatic linking between users and employees

Installation
============

To install this module, you need to:

#. Ensure dependencies are installed: ``base_tier_validation``, ``hr``
#. Clone the repository
#. Add the module to your addons path
#. Update the module list
#. Install the module from Apps menu

Dependencies
============

This module depends on:

* ``base_tier_validation``: Core tier validation framework
* ``hr``: Human Resources module

Configuration
=============

After installation:

#. Configure employee roles and positions in HR module
#. Set up department structure and reporting relationships
#. Create tier definitions using employee roles
#. Test approval workflows with different employee scenarios
#. Configure notification and escalation rules

**Employee Setup**

#. Ensure all employees have proper job positions assigned
#. Set up manager-employee relationships
#. Configure department assignments
#. Define employee roles and responsibilities

**Tier Definition Configuration**

#. Navigate to Settings > Technical > Tier Validation > Tier Definition
#. Create new tier definitions or modify existing ones
#. Add employee role criteria to approval rules
#. Configure department-based approval routing
#. Set up position-based approval requirements

Usage
=====

**Creating HR-based Tier Definitions**

#. Access tier definition configuration
#. Create a new tier definition for your document type
#. Select "Employee Role" as one of the approval criteria
#. Choose specific roles, departments, or positions
#. Configure additional validation rules as needed
#. Test the approval workflow

**Approval Workflow Examples**

**Example 1: Department Manager Approval**
* Tier 1: Direct manager approval
* Tier 2: Department manager approval
* Tier 3: HR manager approval for amounts > $1000

**Example 2: Position-based Approval**
* Tier 1: Team lead approval for routine requests
* Tier 2: Department head for significant requests
* Tier 3: C-level for strategic decisions

**Example 3: Role-specific Workflow**
* Tier 1: Project manager for project-related expenses
* Tier 2: Finance manager for budget validation
* Tier 3: General manager for final approval

Advanced Configuration
======================

**Complex Approval Logic**

Create sophisticated approval rules combining:

* Employee roles and positions
* Department membership
* Reporting relationships
* Amount thresholds
* Document types
* Custom business rules

**Dynamic Approver Assignment**

* Automatic approver assignment based on employee hierarchy
* Fallback approvers when primary approvers are unavailable
* Delegation rules for temporary assignments
* Escalation procedures for delayed approvals

**Integration with Other Modules**

This module can be combined with other tier validation modules:

* Purchase tier validation
* Expense tier validation
* Invoice tier validation
* Custom document validation

Workflow Examples
=================

**HR Document Approval**

1. **Employee Request**: Employee submits request (expense, leave, etc.)
2. **Automatic Routing**: System determines approvers based on employee role/department
3. **Manager Review**: Direct manager receives notification for approval
4. **Department Approval**: Department head approval for significant amounts
5. **HR Validation**: HR team final validation for policy compliance
6. **Completion**: Request approved and processed

**Purchase Request Approval**

1. **Requester Submission**: Employee submits purchase request
2. **Team Lead Review**: Team lead approval for standard requests
3. **Department Manager**: Department manager for budget validation
4. **Procurement Team**: Procurement team for vendor management
5. **Finance Approval**: Finance team for final budget approval

Benefits for Organizations
==========================

**Improved Compliance**

* Ensure proper approval hierarchy is followed
* Maintain audit trail for all approvals
* Enforce organizational policies automatically
* Reduce compliance risks

**Enhanced Efficiency**

* Automatic approval routing based on organization structure
* Reduce manual approval assignment
* Faster processing with clear approval paths
* Reduced bottlenecks in approval processes

**Better Control**

* Clear separation of duties based on roles
* Appropriate approval levels for different transaction types
* Flexible configuration for changing organizational needs
* Comprehensive reporting on approval activities

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