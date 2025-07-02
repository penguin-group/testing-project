==========
PISA Sites
==========

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-OPL--1-blue.png
    :target: https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps-licenses
    :alt: License: OPL-1
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/pisa_sites
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

Manage sites and related information for PISA's infrastructure projects, including capacity tracking, voltage monitoring, and project progress management.

**Table of contents**

.. contents::
   :local:

Features
========

* **Site Management**: Comprehensive site information tracking and management
* **State Management**: Configurable site states with workflow support
* **Tag System**: Flexible tagging system for site categorization
* **Capacity Tracking**: Monitor site capacity in megawatts (MW)
* **Voltage Level Monitoring**: Track voltage levels for electrical infrastructure
* **Probability Assessment**: Project probability tracking with percentage scoring
* **Priority Management**: Priority-based site organization and management
* **Project Brief**: Rich text project documentation and briefing
* **Mail Integration**: Communication and activity tracking for sites

Overview
========

PISA Sites is a comprehensive site management system designed specifically for infrastructure projects. It provides tools to track, monitor, and manage various aspects of site development including technical specifications, project progress, and administrative details.

This module is particularly useful for energy, telecommunications, or other infrastructure companies that need to manage multiple sites with varying characteristics and development stages.

Key Models
==========

**Site (pisa.site)**

Main model representing a site with comprehensive tracking capabilities:

* **Basic Information**: Name, description, and identification
* **Geographic Data**: Country and location information
* **Technical Specifications**: Capacity and voltage level tracking
* **Project Management**: Probability, priority, and progress tracking
* **Documentation**: Project briefs and detailed information
* **Communication**: Mail thread and activity tracking

**Site State (pisa.site.state)**

Configurable states for site workflow management:

* **Custom States**: Define custom states for your workflow
* **State Transitions**: Manage site progression through different states
* **Default States**: Pre-configured common states (New, In Progress, Done, Cancelled)

**Site Tag (pisa.site.tag)**

Flexible tagging system for site categorization:

* **Color-coded Tags**: Visual tag identification with color coding
* **Hierarchical Organization**: Organize sites by multiple tag dimensions
* **Flexible Categorization**: Create custom tag categories as needed

Site Management Features
========================

**Workflow Management**

* **State Progression**: Track sites through development stages
* **Priority Levels**: Four-level priority system (Low, Medium, High, Very High)
* **Probability Scoring**: Track project success probability (0-100%)
* **Status Tracking**: Real-time status updates and progress monitoring

**Technical Specifications**

* **Capacity Monitoring**: Track site capacity in megawatts (MW)
* **Voltage Level Tracking**: Monitor electrical voltage levels (V)
* **Technical Documentation**: Maintain technical specifications and requirements
* **Compliance Tracking**: Ensure sites meet technical requirements

**Project Documentation**

* **Project Briefs**: Rich HTML project descriptions and documentation
* **Communication History**: Complete communication thread for each site
* **Activity Tracking**: Monitor all activities and changes
* **Document Management**: Centralized document storage and management

Installation
============

To install this module, you need to:

#. Ensure dependencies are installed: ``base``, ``mail``
#. Clone the repository
#. Add the module to your addons path
#. Update the module list
#. Install the module from Apps menu

Dependencies
============

This module depends on:

* ``base``: Core Odoo functionality
* ``mail``: Communication and activity tracking

Configuration
=============

After installation:

#. Configure site states according to your workflow
#. Set up site tags for categorization
#. Configure user permissions and access rights
#. Set up default values and validation rules
#. Customize views and reports as needed

**Site States Configuration**

#. Go to Sites > Configuration > Site States
#. Create custom states for your workflow
#. Define state transitions and rules
#. Set up default states for new sites

**Tag Configuration**

#. Navigate to Sites > Configuration > Site Tags
#. Create tag categories for your organization
#. Set up color coding for visual identification
#. Define tag hierarchies if needed

**Security Configuration**

#. Configure user groups and permissions
#. Set up record rules for data access
#. Define approval workflows if required
#. Test access controls with different user roles

Usage
=====

**Creating and Managing Sites**

#. Navigate to Sites > Sites
#. Click "Create" to add a new site
#. Fill in basic information (name, description)
#. Set geographic and technical information
#. Configure project management details
#. Add tags and set initial state
#. Save and begin tracking

**Site Workflow Management**

#. Track sites through different development stages
#. Update probability scores as projects progress
#. Adjust priority levels based on business needs
#. Monitor capacity and voltage requirements
#. Maintain project documentation and briefs

**Communication and Activities**

#. Use the mail thread for site communication
#. Schedule and track activities for each site
#. Maintain communication history
#. Set up notifications and alerts
#. Collaborate with team members

Site Monitoring
===============

**Capacity Tracking**

* Monitor total capacity across all sites
* Track capacity by state, tag, or priority
* Generate capacity reports and forecasts
* Plan capacity allocation and development

**Progress Monitoring**

* Track site development progress
* Monitor probability changes over time
* Identify bottlenecks and issues
* Generate progress reports

**Priority Management**

* Organize sites by priority level
* Focus resources on high-priority sites
* Balance workload across different priorities
* Track priority changes and reasons

Reporting and Analytics
=======================

**Site Reports**

* Comprehensive site listings and summaries
* Progress reports by state and priority
* Capacity analysis and forecasting
* Technical specification reports

**Dashboard Views**

* Visual site status dashboard
* Capacity and voltage monitoring panels
* Priority-based site organization
* Progress tracking visualizations

**Custom Reports**

* Configurable report templates
* Export capabilities for external analysis
* Integration with business intelligence tools
* Automated report generation

Security Features
=================

**Access Control**

* Role-based site access permissions
* Record-level security rules
* Field-level access controls
* Company-specific site isolation

**Data Security**

* Audit trail for site changes
* User activity logging
* Data validation and integrity checks
* Backup and recovery support

Integration Capabilities
========================

**Project Integration**

* Integration with project management modules
* Link sites to projects and tasks
* Resource allocation and planning
* Timeline and milestone tracking

**GIS Integration**

* Geographic information system support
* Mapping and location services
* Spatial analysis capabilities
* Location-based reporting

**External Systems**

* API support for external integrations
* Data import/export capabilities
* Third-party system connectivity
* Automated data synchronization

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

* William Eckerleben <william@penguin.digital>

Maintainers
~~~~~~~~~~~

This module is maintained by Penguin Infrastructure.

.. image:: https://penguin.digital/logo.png
   :alt: Penguin Infrastructure
   :target: https://penguin.digital

Penguin Infrastructure is a software development company specialized in Odoo implementations. 