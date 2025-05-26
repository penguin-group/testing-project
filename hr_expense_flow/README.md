# HR Expense Flow

## Overview

This module extends Odoo's HR Expense functionality to provide customized expense management workflows. It modifies how expense reports are processed and managed within Odoo.

## Features

- Custom expense workflows and processing
- Enhanced company configuration options
- Extended expense report functionality

## Installation
The module can be installed like any other Odoo module through the Apps menu in Odoo.

## Configuration

After installation:
1. Go to Settings > Expenses > Accounting
2. Configure the expense journals and accounts

## Usage

### Creating an Expense

1. Navigate to Expenses > My Expenses
2. Click "New" to create a new expense record
3. Fill in the required information:

### Automatic Processing for Company-Paid Expenses

1. The system automatically generates:
    - A vendor bill
    - A clearing journal entry (acting as payment)
2. The expense moves to "To Post" status


### Accounting Review Process

The accounting team should:
1. Review the generated vendor bill
2. Validate the vendor bill
3. Match the clearing entry with the vendor bill
4. Post the related journal entries

### Tracking Status

You can track the expense status through:
- My Expenses dashboard
- Accounting > Vendor Bills
- Accounting > Journal Entries

## Contributing

Please submit issues and pull requests to the repository.

## Author

**Penguin Infrastructure S.A.**
- Website: https://penguin.digital

## Support

For support and inquiries, please contact:
- Email: [support email]
- Website: https://penguin.digital

## License

This module is licensed under OPL-1.