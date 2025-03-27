# QuickenQIFImport

A Python utility for converting between QIF (Quicken Interchange Format) and CSV formats for financial transaction data.

## Overview

QuickenQIFImport is a utility designed to import QIF (Quicken Interchange Format) files into Quicken or Quicken-compatible applications and convert between QIF and CSV formats. This tool serves financial software users who need to transfer transaction data, account information, and financial categories from systems that export QIF files.

The application provides both a command-line interface (CLI) and a graphical user interface (GUI), allowing users to:

- Convert CSV files to QIF format for importing into Quicken
- Convert QIF files to CSV format for analysis or importing into other systems
- Manage templates for mapping CSV columns to QIF fields
- Preview and validate financial data before conversion

## Features

- **Bidirectional Conversion**: Convert between QIF and CSV formats in both directions
- **Multiple Account Types**: Support for bank, cash, credit card, investment, asset, and liability accounts
- **Investment Transactions**: Handle buy, sell, dividend, and other investment transaction types
- **Template Management**: Create and save custom field mappings for different CSV formats
- **Data Validation**: Validate transaction data to ensure compatibility with Quicken
- **Flexible Date Formats**: Support for multiple date formats in both input and output
- **Split Transactions**: Support for transactions split across multiple categories
- **Command-line Interface**: For batch processing and scripting
- **Graphical User Interface**: For interactive use

## Installation

### Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/mmarcus006/QuickenQIFImport.git
   cd QuickenQIFImport
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Command-line Interface

#### Converting CSV to QIF

```
python -m quickenqifimport csv-to-qif --input input.csv --output output.qif --account-type BANK [--template template.json]
```

#### Converting QIF to CSV

```
python -m quickenqifimport qif-to-csv --input input.qif --output output.csv [--template template.json]
```

#### Creating a Template

```
python -m quickenqifimport create-template --input sample.csv --output template.json --account-type BANK
```

### Graphical User Interface

To start the GUI:

```
python -m quickenqifimport --gui
```

The GUI provides the following functionality:
- File selection for input and output
- Account type selection
- Template management
- Data preview
- Conversion options

## Supported Account Types

- **Bank**: Checking and savings accounts
- **Cash**: Cash transactions
- **Credit Card**: Credit card transactions
- **Investment**: Investment accounts (stocks, mutual funds, etc.)
- **Asset**: Asset accounts (property, vehicles, etc.)
- **Liability**: Liability accounts (loans, mortgages, etc.)

## Supported Investment Transaction Types

- **Buy**: Purchase of securities
- **Sell**: Sale of securities
- **Dividend**: Dividend payments
- **Interest Income**: Interest income
- **Reinvest Dividend**: Reinvestment of dividends
- **Capital Gains**: Long and short-term capital gains

## Template Management

Templates define how CSV columns map to QIF fields. The application includes default templates for common CSV formats, but you can create custom templates for your specific needs.

A template is a JSON file that defines:
- Field mappings between CSV columns and QIF fields
- Date format for parsing dates in the CSV
- Default values for required fields that may be missing in the CSV

## File Format Examples

### QIF Format Example

```
!Type:Bank
D03/15/2023
T-125.00
PGrocery Store
MFood for the week
^
D03/16/2023
T-45.75
PGas Station
MFuel
^
```

### CSV Format Example

```
Date,Amount,Payee,Memo,Category
03/15/2023,-125.00,Grocery Store,Food for the week,Food:Groceries
03/16/2023,-45.75,Gas Station,Fuel,Auto:Fuel
```

## Development

### Running Tests

```
python -m pytest
```

### Code Coverage

```
python -m pytest --cov=src
```

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Documentation

For more detailed information, please refer to the documentation in the `docs/` directory:

- [Product Requirements Document](docs/PRD.md)
- [Implementation Guide](docs/implementation_guide.md)
- [Architecture Overview](docs/architecture-overview.md)
