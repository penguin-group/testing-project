====================
Project GitHub Integration
====================

This module extends Odoo's Project application by integrating it with GitHub. It enables development teams to link Odoo projects to GitHub repositories and automatically synchronize branches, commits, and pull requests, providing full project traceability between Odoo and GitHub.

Key Features
============
- Link Odoo projects to GitHub repositories.
- Automatically synchronize GitHub branches, commits, and pull requests with Odoo tasks.
- View and manage GitHub branches, commits, and pull requests directly from the Odoo UI.
- Associate GitHub branches and PRs with specific Odoo tasks using task codes in branch names.
- Configure GitHub organization and access token at the company/settings level.
- Scheduled cron job keeps GitHub data in sync with Odoo.

Usage
=====
1. Install the module from the Apps menu.
2. In the Project Settings, configure your GitHub organization and personal access token.
3. Mark a project as a "Development Project" and select a repository to link.
4. Odoo will automatically fetch and sync branches, commits, and pull requests from the linked repository.
5. Use the project and task views to see related GitHub data and open detailed views for branches, commits, and PRs.
6. Use the provided wizard to create new GitHub branches from Odoo tasks.

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

* José González <jose.gonzalez@penguin.digital>

Maintainers
~~~~~~~~~~~

This module is maintained by Penguin Infrastructure.

.. image:: https://penguin.digital/logo.png
   :alt: Penguin Infrastructure
   :target: https://penguin.digital

Penguin Infrastructure is a software development company specialized in Odoo implementations.
