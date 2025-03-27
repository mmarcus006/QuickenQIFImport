# QuickenQIFImport

A versatile and user-friendly desktop application for converting financial transaction data between CSV templates and Quicken Interchange Format (QIF) files.

## Overview

QuickenQIFImport is a Python-based utility designed to simplify the process of importing financial data into Quicken or other financial management software that supports the QIF format. It provides both a graphical user interface and a command-line interface for converting between CSV and QIF formats.

## Features

- **Bidirectional Conversion**: Convert from CSV to QIF and from QIF to CSV
- **Multiple Account Types**: Support for bank, cash, credit card, investment, asset, and liability accounts
- **Customizable Templates**: Create and manage CSV templates for different financial institutions
- **Investment Transactions**: Full support for investment transactions including buys, sells, dividends, and more
- **Transfer Detection**: Automatically identify and link transfer transactions between accounts
- **Data Validation**: Comprehensive validation of input data to ensure accuracy
- **User-Friendly Interface**: Intuitive GUI with drag-and-drop support
- **Command-Line Support**: Powerful CLI for batch processing and automation

## Installation

### Prerequisites

- Python 3.9 or higher
- PyQt6 (for GUI)
- Pydantic 2.x

### Install from PyPI

```bash
pip install quickenqifimport
```

### Install from Source

```bash
git clone https://github.com/mmarcus006/QuickenQIFImport.git
cd QuickenQIFImport
pip install -e .
```

## Usage

### Graphical User Interface

Launch the GUI application:

```bash
quickenqifimport-gui
```

### Command Line Interface

Convert a CSV file to QIF:

```bash
quickenqifimport input.csv output.qif --type bank --template my_bank_template
```

Convert a QIF file to CSV:

```bash
quickenqifimport input.qif output.csv --type investment --template my_investment_template
```

List available templates:

```bash
quickenqifimport --list-templates
```

## Supported File Formats

### CSV Format

The application supports custom CSV templates that can be configured to match various financial institution export formats. Default templates are provided for common formats.

### QIF Format

Supports the Quicken Interchange Format (QIF) specification, including:

- Bank, cash, and credit card transactions
- Investment transactions
- Categories and classes
- Account information
- Memorized transactions

## Templates

Templates define how CSV files are mapped to QIF fields. They can be created and managed through the GUI or defined in YAML files.

Example template structure:

```yaml
name: my_bank_template
account_type: Bank
field_mapping:
  date: Date
  amount: Amount
  payee: Description
  category: Category
  memo: Notes
delimiter: ","
has_header: true
date_format: "%Y-%m-%d"
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/mmarcus006/QuickenQIFImport.git
cd QuickenQIFImport
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Check Code Coverage

```bash
pytest --cov=quickenqifimport
```

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.
