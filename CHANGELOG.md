# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Tier validation for Purchase Agreements

### Changed
- 

### Fixed
- 

## [3.4.0.1] - 2025-04-21

### Fixed
- Fixed RPC_ERROR in balance sheet report by defining missing ACCOUNT_CODES_ENGINE_SPLIT_REGEX
- Resolved crash on Tax Report (BO) by correcting currency table method
- Prevented AttributeError during invoice confirmation due to missing name
- Added validation for invoice authorization only on vendor bill posting

## [3.4.0] - 2025-04-07

### Added
- Invoice Confirmation functionality for Head of Finance
- Enhanced procurement process with RFQ to PO workflow
- Finance JR Accountant permission to assign group assets
- Invoice number format validation for Paraguayan companies
- Enhanced vendor bill creation for company-paid expenses
- Certificate enhancements in billing and permissions
- Purchase request alternatives and RFQ improvements
- Enhanced RFQ to PO workflow with new states and fields
- Attachment transfer from purchase requests to RFQs
- Extra costs linking to purchase orders
- Data transfer from main RFQ to alternative RFQ
- Notification and proof of payment upload post-finance completion
- Approval workflow for RFQ to PO process
- Warning on missing analytic account in purchase request product line
- Certificates of completion for purchase orders
- Purchase request enhancements

## [3.3.0] - 2025-03-25

### Added
- Enhanced accounting groups functionality
- Migrated and cleaned code for Sites module
- Multicurrency revaluation report for secondary currency support
- Automated end-of-month exchange rate adjustments
- Temporary module to reset journal entries and fix secondary balance errors

### Changed
- Updated access rights for Confirm button
- Enhanced access rights for junior accountant
- Improved currency filter button alignment
- Added assets support for secondary currency reports

## [3.2.0] - 2025-03-07

### Added
- Enhanced user management for finance
- Operative profit and loss report
- Improved report export styling for PDF and XLSX
- Analytic distribution column for fixed assets
- Enhanced bank reconciliation components
- Account change lock date wizard with CFO permissions
- Source report field for analytic account vertical grouping
- Validation for analytic distribution in bank reconciliation
- 'Requires Analytic Account' field to product template
- Enhanced invoice approval permissions
- Security rules for invoice authorization
- Enhanced PDF export templates and styling
- Vertical grouping of analytic accounts in account reports
- Analytic account hierarchy in account report lines
- Custom account report handlers and styles
- Enhanced secondary balance handling
- Automated account reconciliation for aged payable reporting
- Analytic accounts requirement for bills, invoices, payments, and journal entries
- Partner view XML for accounting entries visibility
- Default values for new invoice authorization from vendor bills
- Self-printed invoice functionality in a new module
- Validation to prevent posting of unbalanced secondary balances

### Fixed
- Incorrect currency symbol when printing finance report
- Payment reconciliation issues in journal entry
- Invoice authorization numbers not displaying in supplier bills
- Currency change impacts on bills linked to assets
- Partial line handling in reconciliation logic
- Invoice currency rate calculation
- Reconciliation process for bank accounts

## [3.1.0] - 2025-01-06

### Added
- Self-printed invoice functionality in a new module
- Partner view XML for accounting entries visibility
- Default values for new invoice authorization from vendor bills

### Changed
- Removed invoice_currency_rate module from repository

### Fixed
- Added validation to prevent posting of unbalanced secondary balances

## [3.0.0.1] - 2025-01-03

### Fixed
- Allowed CI as VAT numbers for individual customers in Paraguay

## [3.0.0] - 2024-12-24

### Added
- Upgraded secondary currency module to version 18.0
- Upgraded l10n_py module to version 18.0
- Implemented feature logging system in Odoo
- Added cron job to compute the validity of invoice authorizations
- Custom properties for product categories and stock lots

### Changed
- Refactored Payment model to align with version 18.0 code
- Ensured float fields display correct decimal places when tracking changes
- Converted all pisa-addons modules to version 18.0
- Updated field names due to changes in v18.0

### Fixed
- Ensured currency selector compatibility with version 18.0 in accounting reports
- Fixed width of the PDF viewer in book registration report
- Fixed error in book registration report download
- Adjusted module for compatibility with Odoo 18
- Corrected value causing module installation failure
- Fixed book registration report generation

## [2.1.1] - 2024-12-16

### Added
- Initial release of version 2.1.1

## [2.1.0] - 2024-12-16

### Added
- Initial release of version 2.1.0

## [2.0.0.3] - 2024-12-16

### Added
- Initial release of version 2.0.0.3

## [2.0.0.2] - 2024-12-11

### Added
- Initial release of version 2.0.0.2

## [2.0.0.1] - 2024-12-10

### Added
- Initial release of version 2.0.0.1

## [2.0.0] - 2024-12-04

### Added
- Initial release of version 2.0.0

## [1.1.0.6] - 2024-11-13

### Added
- Initial release of version 1.1.0.6

## [1.1.0.5] - 2024-10-09

### Added
- Initial release of version 1.1.0.5

## [1.1.0.4] - 2024-10-07

### Added
- Initial release of version 1.1.0.4

## [1.1.0.3] - 2024-09-27

### Added
- Initial release of version 1.1.0.3

## [1.1.0.2] - 2024-09-26

### Added
- Initial release of version 1.1.0.2

## [1.1.0.1] - 2024-09-17

### Added
- Initial release of version 1.1.0.1

## [1.1.0] - 2024-09-11

### Added
- Initial release of version 1.1.0

## [1.0.0.3] - 2024-09-11

### Added
- Initial release of version 1.0.0.3

## [1.0.0.2] - 2024-09-09

### Added
- Initial release of version 1.0.0.2

## [1.0.0.1] - 2024-09-06

### Added
- Initial release of version 1.0.0.1

## [1.0.0] - 2024-09-06

### Added
- Initial release of version 1.0.0 