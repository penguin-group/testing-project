========================
Agreement
========================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-OPL--1-blue.png
    :target: https://www.odoo.com/documentation/master/legal/licenses.html#odoo-apps-licenses
    :alt: License: OPL-1
.. |badge3| image:: https://img.shields.io/badge/github-penguin%2Fpisa--addons-lightgray.png?logo=github
    :target: https://github.com/penguin-group/pisa-addons/tree/master/account_custom_currency_rate
    :alt: penguin-group/pisa-addons

|badge1| |badge2| |badge3|

Legal agreements management for Odoo.

**Table of contents**

.. contents::
   :local:

Features
========

* **Legal Agreements Metadata Tracking**: Every metadata found in an agreement is correctly tracked by logging all modifications on the chatter.
* **Default Kanban View Grouped by Stage**: When entering the module, the user sees the agreements grouped by their stage.
* **Users May Create Their Own Agreement Types**: On a "Settings" menu, the user is able to create, edit, and remove legal process types, terms, tags, agreement types, etc.
* **Agreements Have Relevant Milestones**: An agreement can be expanded with relevant milestones created by the user in order to track deadlines and to check if the milestone was reached or not.
* **Automated email notifications**: Legal officers and admins get notifications to know about incoming deadlines related to agreements and milestones.


Overview
========

This module adds a new app for agreements management to Odoo. Besides having an agreement object with basic metadata, this module also includes models for agreement stages, types, legal processes, milestones, jurisdictions, tags and terms.

Key Components
==============

**Agreement**

* An agreement may be related to others (it is a many2many relationship). This is tracked on the "Document Management" tab.
* An agreement may have several partners
* An agreement may have several milestones

**Agreement Stages**

* Stages are created only by users in the "Administration: Settings" group.
* These stages may be active or inactive, be folded in the kanban view, and be arranged depending on their sequence number.

**Milestones**

* A milestone can be related to only one agreement
* Although not mandatory, a milestone may have a deadline
* Users can track if the milestones were reached or not


Models
========

* **Agreement (agreement)**
* **Agreement Stage (agreement.stage)**
* **Agreement Type (agreement.type)**
* **Agreement Tag (agreement.tag)**
* **Agreement Renewal Term (agreement.renewal.term)**
* **Agreement Milestone (agreement.milestone)**
* **Agreement Legal Process Type (agreement.legal.process.type)**
* **Agreement Jurisdiction (agreement.jurisdiction)**

Installation
============

To install this module, you need to:

#. Clone the pisa_addons repository if you haven't already. In case you do have the pisa_addons repo but you still don't see this module, make sure to ``git pull`` and get the latest version of pisa_addons.
#. Ensure dependencies are installed: ``base``, ``web``, ``mail``
#. Update the module list
#. Install the module from Apps menu

Dependencies
============

This module depends on:

* ``base``: Core Odoo functionality
* ``web``: Web interface components
* ``mail``: Communication, discussion, and tracking through the chatter

Configuration
=============

**User Permissions Setup**

#. Go to Settings > Users & Companies > Groups
#. Choose either "Agreement: Administration", "Agreement: Legal Officer", or "Agreement: Read-only"
#. In the Users tab, select the users that may be part of the given access group

Language Support
================

This module includes:

* **Spanish Language Pack**: Complete Spanish translation (``i18n/es.po``)

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

* David Paez <david@penguin.digital>

Maintainers
~~~~~~~~~~~

This module is maintained by Penguin Infrastructure.

.. image:: https://penguin.digital/logo.png
   :alt: Penguin Infrastructure
   :target: https://penguin.digital

Penguin Infrastructure is a software development company specialized in Odoo implementations. 