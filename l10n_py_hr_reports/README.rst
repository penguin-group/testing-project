====================
Paraguayan HR Reports
====================

Overview
========
This module extends the payroll reporting functionality in Odoo by
adding official reports required in Paraguay.

It provides:

* **MTESS reports** (spreadsheets required by the Ministry of Labor):
  - **Planilla de Empleados y Obreros**
  - **Planilla de Sueldos y Jornales**
  - **Resumen General de Personal Ocupado**

* **IPS report** (text file required by the Instituto de Previsión Social):
  - Generates a `.txt` file compatible with the **REI** web application for data import.

Key Features
============ 
* Two new menu entries under *Payroll > Reporting*:
  - **MTESS Reports**
  - **IPS Report**
* MTESS wizard:
  - Allows the user to select a **year**
  - Generates all three official MTESS spreadsheets
* IPS wizard:
  - Allows the user to select a **year** and a **month**
  - Generates a `.txt` file compatible with the **REI** web application
* Reports are stored and grouped by year in the list view
* Exportable for compliance purposes (Excel and TXT)

Usage
=====
**MTESS Reports**
1. Navigate to *Payroll > Reporting > MTESS Reports*.
2. Press the **Generate Report** button.
3. In the **Generate MTESS Report** wizard:
   * Select the **Year**.
   * Press **Generate Report**.
4. Three spreadsheets will be created:
   * Planilla de Empleados y Obreros
   * Planilla de Sueldos y Jornales
   * Resumen General de Personal Ocupado
5. The list view is grouped by year for easier navigation.

**IPS Report**
1. Navigate to *Payroll > Reporting > IPS Report*.
2. Press the **Generate Report** button.
3. In the **Generate IPS Report** wizard:
   * Select the **Year** and **Month**.
   * Press **Generate Report**.
4. A `.txt` file will be created, compatible with the **REI** web application.
5. The list view is grouped by year for easier navigation.



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
