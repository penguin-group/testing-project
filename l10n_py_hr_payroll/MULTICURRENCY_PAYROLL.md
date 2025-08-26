# Multi-Currency Payroll Implementation for Paraguay

## Overview

This module implements comprehensive multi-currency support for Odoo's payroll system, specifically designed for Paraguayan companies that need to handle contracts in different currencies than the company's base currency.

## Key Features

### 1. Contract-Level Currency Selection
- **Field**: `contract_currency_id` on `hr.contract`
- **Purpose**: Allows setting a specific currency for each contract, independent of company currency
- **Impact**: All wage calculations, payslip generation, and accounting entries respect this currency

### 2. Automatic Currency Flow
```
Contract Currency (PYG) 
    ↓
Payslip Currency (PYG) 
    ↓
Payslip Line Amounts (PYG)
    ↓
Journal Entry Lines:
    - debit/credit (USD - company currency)
    - amount_currency (PYG - original amount)
    - currency_id (PYG - foreign currency)
```

### 3. Multi-Currency Accounting Integration

#### Journal Entry Structure
When a payslip is confirmed, journal entries are created with:
- **Company Currency**: `debit` and `credit` fields converted to company currency
- **Foreign Currency**: `amount_currency` field with original contract currency amounts
- **Currency Reference**: `currency_id` field pointing to the contract currency

#### Example Journal Entry
```
Account: Salary Expense
    debit: $2,000 USD (company currency)
    credit: $0 USD
    amount_currency: ₲15,000,000 PYG (contract currency)
    currency_id: PYG

Account: Payable to Employee  
    debit: $0 USD
    credit: $2,000 USD (company currency)
    amount_currency: -₲15,000,000 PYG (contract currency)
    currency_id: PYG
```

## Implementation Details

### Core Models Extended

#### 1. `hr.contract`
- **New Field**: `contract_currency_id`
- **Override**: `wage` field to use `currency_field='contract_currency_id'`
- **Override**: `currency_id` computed field to derive from `contract_currency_id`
- **Methods**: Currency conversion utilities

#### 2. `hr.payslip`
- **Override**: `currency_id` computed from contract currency
- **Override**: `_get_localdict()` to add currency conversion utilities to salary rules
- **Enhancement**: Currency-aware calculations

#### 3. `hr.payslip` (Accounting Extension)
- **Override**: `_prepare_line_values()` for multi-currency journal lines
- **Override**: `_prepare_slip_lines()` for currency-aware accounting
- **Enhancement**: Proper `amount_currency` and `currency_id` handling

### Currency Conversion Logic

#### Payroll Calculations
- Salary rules execute in **contract currency**
- Wage, allowances, deductions calculated in **contract currency**
- Payslip totals displayed in **contract currency**

#### Accounting Entries
- Journal line amounts converted to **company currency**
- Original amounts preserved in `amount_currency` field
- Foreign currency properly tracked for reporting

### Paraguay-Specific Enhancements

#### Salary Rule Utilities
The `_get_localdict()` method adds currency utilities to salary rule calculations:

```python
# Available in salary rule Python code:
contract_currency    # The contract's currency object
company_currency     # The company's currency object
convert_to_company   # Function to convert amount to company currency
convert_from_company # Function to convert amount to contract currency
```

#### Usage in Salary Rules
```python
# Example salary rule calculation
result = contract.wage * (worked_days['WORK100'].number_of_days / 30)

# Convert to company currency if needed
result_company = convert_to_company(result)

# The result stays in contract currency, conversion happens in accounting
```

## Configuration

### 1. Enable Multi-Currency
1. Go to **Accounting > Configuration > Settings**
2. Enable **Multi-Currencies**
3. Configure exchange rates

### 2. Set Contract Currency
1. Go to **HR > Contracts**
2. Open a contract
3. Set **Contract Currency** field
4. **Wage** field will automatically display in the selected currency

### 3. Verify Payroll Journal
The module automatically creates a "Nómina Paraguay" journal that:
- Handles multi-currency entries
- Uses appropriate expense accounts
- Maintains currency tracking

## Benefits

### For Accountants
- **Proper Currency Tracking**: All foreign currency amounts preserved
- **Compliance**: Meets international accounting standards
- **Reporting**: Currency gains/losses properly tracked
- **Audit Trail**: Clear foreign currency transaction history

### For HR Managers
- **Flexible Contracts**: Set wages in any currency
- **Accurate Calculations**: Payroll computed in contract currency
- **Clear Payslips**: Employees see amounts in their contract currency
- **Easy Management**: No manual currency conversions needed

### For System Administrators
- **Automatic Conversion**: Exchange rates applied automatically
- **Data Integrity**: No duplicate currency handling
- **Scalable**: Works with any number of currencies
- **Integration**: Seamless with Odoo's core accounting

## Technical Notes

### Currency Rate Management
- Exchange rates pulled from Odoo's standard currency system
- Rates applied based on payslip date
- Historical rates preserved for audit purposes

### Performance Considerations
- Currency conversions cached during payslip generation
- Minimal additional database queries
- Efficient bulk processing for payroll batches

### Error Handling
- Validation for missing exchange rates
- Fallback to company currency if contract currency unavailable
- Clear error messages for currency configuration issues

## Future Enhancements

### Potential Additions
- Secondary currency reporting for Paraguay
- Currency hedging tracking
- Multi-currency employee loans
- Foreign currency expense reimbursements

### Integration Opportunities
- Bank integration for multi-currency payments
- Government reporting in specific currencies
- International payroll synchronization