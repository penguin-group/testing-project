====================
Paraguay HR Payroll
====================

Paraguayan Payroll Module
==========================

This module provides specific functionalities for payroll processing in Paraguay, complying with local regulations.

Key Features
============

**Salary Calculations**

* Proportional salary based on days worked
* Daytime overtime (50% additional)
* Nighttime overtime (100% additional + 30% night surcharge)
* Night surcharges (30% additional)
* Holiday work (200% daytime, 230% nighttime)
* Medical leave (50% company reimbursement for 2-3 days)
* Proportional vacation pay

**Allowances and Benefits**
 
* Family allowance (children under 17 years old)
* Childcare subsidy (children under 3 years old)
* Other sporadic income
* Additional bonuses

**Deductions and Withholdings**

* Employee IPS (9% of taxable base)
* Salary advances
* Judicial garnishment (maximum 25%)
* Medical insurance
* Solidarity contributions
* Various deductions (training, parking, English, loans)

**System Features**

* Integration with Paraguayan accounting localization (l10n_py)
* Payslip reports with Paraguayan format
* Date-configurable parameters
* Multiple salary structures
* Automatic validation of legal limits

Configuration
=============

**Installation**

1. Ensure you have the base modules installed:
   - hr_payroll (Enterprise)
   - hr_work_entry_contract
   - l10n_py

2. Install the pisa_hr_payroll module

**Initial Setup**

1. **Employees**: Configure Paraguay-specific information in the employee form:
   - IPS number
   - Children information (for family allowances)
   - Bank account and payment method

2. **Contracts**: Configure specific parameters in contracts:
   - Vacation days per year
   - Medical insurance contribution
   - Judicial garnishment percentages
   - Additional allowances

3. **Parameters**: Review and adjust system parameters:
   - Minimum wage
   - IPS rates
   - Family allowance amounts
   - Overtime and surcharge rates

Usage
=====

**Payroll Processing**

1. Go to Payroll > Payslips
2. Create a new payslip or use "Generate Payslips"
3. Select the "Paraguay Monthly Settlement" structure
4. Configure additional inputs as needed:
   - Overtime hours
   - Vacation days
   - Medical leave
   - Bonuses and other income
   - Various deductions

5. Compute the payslip to generate lines automatically
6. Review and confirm the payslip
7. Generate the report in Paraguayan format

**Reports**

The module includes a payslip report that replicates the standard Paraguayan format with:
- Employee and company information
- Detailed breakdown of income and deductions
- IPS calculations and totals
- Legal observations and considerations

Support
=======

For technical support, contact:

* **Penguin Infrastructure S.A.**
* Website: https://penguin.digital
* Version: 18.0.1.0.0
* License: OPL-1

Author
======

Developed by Penguin Infrastructure S.A. for payroll processing in Paraguay following local labor regulations.
