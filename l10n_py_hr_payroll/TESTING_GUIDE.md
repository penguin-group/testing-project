# Multi-Currency Payroll Testing Guide

## Prerequisites

1. **Install Module**: Upgrade `pisa_hr_payroll` module
2. **Enable Multi-Currency**: 
   - Go to Accounting > Configuration > Settings
   - Enable "Multi-Currencies"
3. **Configure Exchange Rates**:
   - Go to Accounting > Configuration > Currencies
   - Set up PYG and USD exchange rates

## Test Scenario 1: Basic Multi-Currency Contract

### Setup
1. Create employee: "Juan Pérez"
2. Create contract:
   - Employee: Juan Pérez
   - Wage: ₲15,000,000 PYG
   - Contract Currency: **PYG** (Paraguayan Guaraní)
   - Structure: "Liquidación Mensual Paraguay"

### Expected Results
- Contract wage displays: **₲15,000,000**
- Contract currency field shows: **PYG**
- Wage field uses PYG symbol and formatting

## Test Scenario 2: Payslip Generation

### Process
1. Go to Payroll > Payslips
2. Create new payslip for Juan Pérez
3. Compute payslip

### Expected Results
- Payslip currency: **PYG**
- All amounts in PYG format
- Basic salary: **₲15,000,000**
- Net salary: Calculated in PYG

## Test Scenario 3: Journal Entry Verification

### Process
1. Confirm the payslip (action_payslip_done)
2. Go to the generated journal entry
3. Check journal lines

### Expected Journal Entry Structure
```
Salary Expense Account:
- Debit: $10,000 USD (converted)
- Credit: $0 USD
- Currency: PYG
- Amount Currency: ₲15,000,000

Employee Payable Account:
- Debit: $0 USD  
- Credit: $10,000 USD (converted)
- Currency: PYG
- Amount Currency: -₲15,000,000
```

## Test Scenario 4: Mixed Currency Environment

### Setup
1. Company currency: **USD**
2. Contract 1: Juan (PYG wage)
3. Contract 2: Maria (USD wage)
4. Generate payslips for both

### Expected Results
- Juan's payslip: All PYG amounts
- Maria's payslip: All USD amounts
- Journal entries: Proper currency conversion for Juan only

## Test Scenario 5: Currency Conversion Validation

### Validation Points
1. **Exchange Rate Applied**: Check that amounts are converted using correct rate
2. **Amount Currency Field**: Verify original currency amounts preserved
3. **Reporting**: Multi-currency reports show correct amounts
4. **Balance**: Journal entries balance in company currency

## Debugging Tools

### Logs
Check system logs for currency conversion messages:
```
Processing multi-currency payslip SLIP001: Contract PYG -> Company USD
```

### SQL Queries
Verify journal lines have currency fields:
```sql
SELECT 
    aml.debit,
    aml.credit, 
    aml.amount_currency,
    cur.name as currency
FROM account_move_line aml
JOIN res_currency cur ON cur.id = aml.currency_id
WHERE aml.move_id IN (
    SELECT move_id FROM hr_payslip WHERE number = 'SLIP001'
);
```

## Common Issues & Solutions

### Issue 1: Wage shows USD instead of PYG
**Solution**: Upgrade module to apply `wage` field currency override

### Issue 2: No currency_id in journal lines  
**Solution**: Check that contract has `contract_currency_id` set

### Issue 3: Wrong conversion rate
**Solution**: Update currency exchange rates for payslip date

### Issue 4: Accounting imbalance
**Solution**: Verify all payslip lines have proper currency handling

## Validation Checklist

- [ ] Contract currency field visible and functional
- [ ] Wage displays in contract currency
- [ ] Payslip amounts in contract currency  
- [ ] Journal entries have currency_id
- [ ] Journal entries have amount_currency
- [ ] Conversion rates applied correctly
- [ ] Multi-currency reports accurate
- [ ] No duplicate accounting entries
- [ ] System performance acceptable