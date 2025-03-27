import pytest
from datetime import datetime

from quickenqifimport.validators.csv_validator import CSVValidator, CSVValidationError
from quickenqifimport.validators.qif_validator import QIFValidator, QIFValidationError
from quickenqifimport.validators.template_validator import TemplateValidator, TemplateValidationError
from quickenqifimport.models.models import (
    CSVTemplate, AccountType, BankingTransaction, InvestmentTransaction,
    QIFFile, AccountDefinition
)

class TestCSVValidator:
    """Tests for the CSVValidator class."""
    
    def test_validate_csv_format(self):
        """Test validating CSV format."""
        csv_content = """Date,Amount,Description,Reference,Notes,Category
2023-01-01,100.50,Grocery Store,123,Weekly groceries,Food:Groceries
2023-01-02,-50.25,Gas Station,,Fill up car,Auto:Fuel
2023-01-03,1200.00,Paycheck,DIRECT DEP,January salary,Income:Salary
"""
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description",
                "number": "Reference",
                "memo": "Notes",
                "category": "Category"
            },
            date_format="%Y-%m-%d"
        )
        
        validator = CSVValidator()
        
        is_valid, errors = validator.validate_csv_format(csv_content, template)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_csv_format_with_missing_header(self):
        """Test validating CSV format with a missing header."""
        csv_content = """2023-01-01,100.50,Grocery Store,123,Weekly groceries,Food:Groceries
2023-01-02,-50.25,Gas Station,,Fill up car,Auto:Fuel
"""
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description",
                "number": "Reference",
                "memo": "Notes",
                "category": "Category"
            },
            date_format="%Y-%m-%d"
        )
        
        validator = CSVValidator()
        
        is_valid, errors = validator.validate_csv_format(csv_content, template)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("header" in str(error).lower() for error in errors)
    
    def test_validate_csv_format_with_missing_required_column(self):
        """Test validating CSV format with a missing required column."""
        csv_content = """Date,Description,Reference,Notes,Category
2023-01-01,Grocery Store,123,Weekly groceries,Food:Groceries
2023-01-02,Gas Station,,Fill up car,Auto:Fuel
"""
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",  # This column is missing in the CSV
                "payee": "Description",
                "number": "Reference",
                "memo": "Notes",
                "category": "Category"
            },
            date_format="%Y-%m-%d"
        )
        
        validator = CSVValidator()
        
        is_valid, errors = validator.validate_csv_format(csv_content, template)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("amount" in str(error).lower() for error in errors)
    
    def test_validate_csv_data(self):
        """Test validating CSV data."""
        csv_content = """Date,Amount,Description,Reference,Notes,Category
2023-01-01,100.50,Grocery Store,123,Weekly groceries,Food:Groceries
2023-01-02,-50.25,Gas Station,,Fill up car,Auto:Fuel
2023-01-03,1200.00,Paycheck,DIRECT DEP,January salary,Income:Salary
"""
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description",
                "number": "Reference",
                "memo": "Notes",
                "category": "Category"
            },
            date_format="%Y-%m-%d"
        )
        
        validator = CSVValidator()
        
        is_valid, errors = validator.validate_csv_data(csv_content, template)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_csv_data_with_invalid_date(self):
        """Test validating CSV data with an invalid date."""
        csv_content = """Date,Amount,Description,Reference,Notes,Category
invalid-date,100.50,Grocery Store,123,Weekly groceries,Food:Groceries
2023-01-02,-50.25,Gas Station,,Fill up car,Auto:Fuel
"""
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description",
                "number": "Reference",
                "memo": "Notes",
                "category": "Category"
            },
            date_format="%Y-%m-%d"
        )
        
        validator = CSVValidator()
        
        is_valid, errors = validator.validate_csv_data(csv_content, template)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("date" in str(error).lower() for error in errors)
    
    def test_validate_csv_data_with_invalid_amount(self):
        """Test validating CSV data with an invalid amount."""
        csv_content = """Date,Amount,Description,Reference,Notes,Category
2023-01-01,not-a-number,Grocery Store,123,Weekly groceries,Food:Groceries
2023-01-02,-50.25,Gas Station,,Fill up car,Auto:Fuel
"""
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description",
                "number": "Reference",
                "memo": "Notes",
                "category": "Category"
            },
            date_format="%Y-%m-%d"
        )
        
        validator = CSVValidator()
        
        is_valid, errors = validator.validate_csv_data(csv_content, template)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("amount" in str(error).lower() for error in errors)
    
    def test_validate_investment_csv_data(self):
        """Test validating investment CSV data."""
        csv_content = """Date,Action,Security,Quantity,Price,Amount,Commission,Description,Memo,Category
2023-01-01,Buy,AAPL,10,150.75,-1507.50,7.50,Broker,Buy Apple stock,Investments:Stocks
2023-01-02,Sell,MSFT,5,250.25,1251.25,6.25,Broker,Sell Microsoft stock,Investments:Stocks
2023-01-03,Div,VTI,,,,0,Vanguard,Dividend payment,Income:Dividends
"""
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.INVESTMENT,
            field_mapping={
                "date": "Date",
                "action": "Action",
                "security": "Security",
                "quantity": "Quantity",
                "price": "Price",
                "amount": "Amount",
                "commission": "Commission",
                "payee": "Description",
                "memo": "Memo",
                "category": "Category"
            },
            date_format="%Y-%m-%d"
        )
        
        validator = CSVValidator()
        
        is_valid, errors = validator.validate_csv_data(csv_content, template)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_investment_csv_data_with_invalid_action(self):
        """Test validating investment CSV data with an invalid action."""
        csv_content = """Date,Action,Security,Quantity,Price,Amount,Commission,Description,Memo,Category
2023-01-01,InvalidAction,AAPL,10,150.75,-1507.50,7.50,Broker,Buy Apple stock,Investments:Stocks
2023-01-02,Sell,MSFT,5,250.25,1251.25,6.25,Broker,Sell Microsoft stock,Investments:Stocks
"""
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.INVESTMENT,
            field_mapping={
                "date": "Date",
                "action": "Action",
                "security": "Security",
                "quantity": "Quantity",
                "price": "Price",
                "amount": "Amount",
                "commission": "Commission",
                "payee": "Description",
                "memo": "Memo",
                "category": "Category"
            },
            date_format="%Y-%m-%d"
        )
        
        validator = CSVValidator()
        
        is_valid, errors = validator.validate_csv_data(csv_content, template)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("action" in str(error).lower() for error in errors)


class TestQIFValidator:
    """Tests for the QIFValidator class."""
    
    def test_validate_qif_format(self):
        """Test validating QIF format."""
        qif_content = """!Type:Bank
D01/15/2023
T100.50
PGrocery Store
N123
MWeekly groceries
LFood:Groceries
^
D02/28/2023
T-50.25
PGas Station
MFill up car
LAuto:Fuel
^
"""
        
        validator = QIFValidator()
        
        is_valid, errors = validator.validate_qif_format(qif_content)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_qif_format_with_missing_type(self):
        """Test validating QIF format with a missing type."""
        qif_content = """D01/15/2023
T100.50
PGrocery Store
N123
MWeekly groceries
LFood:Groceries
^
"""
        
        validator = QIFValidator()
        
        is_valid, errors = validator.validate_qif_format(qif_content)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("type" in str(error).lower() for error in errors)
    
    def test_validate_qif_format_with_missing_transaction_end(self):
        """Test validating QIF format with a missing transaction end marker."""
        qif_content = """!Type:Bank
D01/15/2023
T100.50
PGrocery Store
N123
MWeekly groceries
LFood:Groceries
D02/28/2023
T-50.25
PGas Station
MFill up car
LAuto:Fuel
^
"""
        
        validator = QIFValidator()
        
        is_valid, errors = validator.validate_qif_format(qif_content)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("transaction" in str(error).lower() for error in errors)
    
    def test_validate_qif_data(self):
        """Test validating QIF data."""
        qif_file = QIFFile()
        
        qif_file.accounts = [
            AccountDefinition(name="Checking", type=AccountType.BANK),
            AccountDefinition(name="Investments", type=AccountType.INVESTMENT)
        ]
        
        qif_file.bank_transactions = {
            "Checking": [
                BankingTransaction(
                    date=datetime(2023, 1, 1),
                    amount=100.50,
                    payee="Grocery Store",
                    number="123",
                    memo="Weekly groceries",
                    category="Food:Groceries"
                ),
                BankingTransaction(
                    date=datetime(2023, 1, 2),
                    amount=-50.25,
                    payee="Gas Station",
                    memo="Fill up car",
                    category="Auto:Fuel"
                )
            ]
        }
        
        qif_file.investment_transactions = {
            "Investments": [
                InvestmentTransaction(
                    date=datetime(2023, 1, 3),
                    action="Buy",
                    security="AAPL",
                    quantity=10,
                    price=150.75,
                    amount=-1507.50,
                    commission=7.50,
                    payee="Broker",
                    memo="Buy Apple stock",
                    category="Investments:Stocks"
                )
            ]
        }
        
        validator = QIFValidator()
        
        is_valid, errors = validator.validate_qif_data(qif_file)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_qif_data_with_missing_date(self):
        """Test validating QIF data with a missing date."""
        qif_file = QIFFile()
        
        qif_file.accounts = [
            AccountDefinition(name="Checking", type=AccountType.BANK)
        ]
        
        qif_file.bank_transactions = {
            "Checking": [
                BankingTransaction(
                    date=None,  # Missing date
                    amount=100.50,
                    payee="Grocery Store",
                    number="123",
                    memo="Weekly groceries",
                    category="Food:Groceries"
                )
            ]
        }
        
        validator = QIFValidator()
        
        is_valid, errors = validator.validate_qif_data(qif_file)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("date" in str(error).lower() for error in errors)
    
    def test_validate_qif_data_with_missing_amount(self):
        """Test validating QIF data with a missing amount."""
        qif_file = QIFFile()
        
        qif_file.accounts = [
            AccountDefinition(name="Checking", type=AccountType.BANK)
        ]
        
        qif_file.bank_transactions = {
            "Checking": [
                BankingTransaction(
                    date=datetime(2023, 1, 1),
                    amount=None,  # Missing amount
                    payee="Grocery Store",
                    number="123",
                    memo="Weekly groceries",
                    category="Food:Groceries"
                )
            ]
        }
        
        validator = QIFValidator()
        
        is_valid, errors = validator.validate_qif_data(qif_file)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("amount" in str(error).lower() for error in errors)
    
    def test_validate_investment_qif_data_with_missing_security(self):
        """Test validating investment QIF data with a missing security."""
        qif_file = QIFFile()
        
        qif_file.accounts = [
            AccountDefinition(name="Investments", type=AccountType.INVESTMENT)
        ]
        
        qif_file.investment_transactions = {
            "Investments": [
                InvestmentTransaction(
                    date=datetime(2023, 1, 3),
                    action="Buy",
                    security=None,  # Missing security
                    quantity=10,
                    price=150.75,
                    amount=-1507.50,
                    commission=7.50,
                    payee="Broker",
                    memo="Buy Apple stock",
                    category="Investments:Stocks"
                )
            ]
        }
        
        validator = QIFValidator()
        
        is_valid, errors = validator.validate_qif_data(qif_file)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("security" in str(error).lower() for error in errors)


class TestTemplateValidator:
    """Tests for the TemplateValidator class."""
    
    def test_validate_template(self):
        """Test validating a template."""
        template = CSVTemplate(
            name="Test Template",
            description="Test template description",
            account_type=AccountType.BANK,
            delimiter=",",
            date_format="%Y-%m-%d",
            has_header=True,
            skip_rows=0,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description",
                "number": "Reference",
                "memo": "Notes",
                "category": "Category"
            }
        )
        
        validator = TemplateValidator()
        
        is_valid, errors = validator.validate_template(template)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_template_with_missing_name(self):
        """Test validating a template with a missing name."""
        template = CSVTemplate(
            name="",  # Missing name
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description"
            }
        )
        
        validator = TemplateValidator()
        
        is_valid, errors = validator.validate_template(template)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("name" in str(error).lower() for error in errors)
    
    def test_validate_template_with_missing_required_field_mapping(self):
        """Test validating a template with a missing required field mapping."""
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "payee": "Description"
            }
        )
        
        validator = TemplateValidator()
        
        is_valid, errors = validator.validate_template(template)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("amount" in str(error).lower() for error in errors)
    
    def test_validate_investment_template(self):
        """Test validating an investment template."""
        template = CSVTemplate(
            name="Test Investment Template",
            account_type=AccountType.INVESTMENT,
            field_mapping={
                "date": "Date",
                "action": "Action",
                "security": "Security",
                "quantity": "Quantity",
                "price": "Price",
                "amount": "Amount",
                "commission": "Commission"
            }
        )
        
        validator = TemplateValidator()
        
        is_valid, errors = validator.validate_template(template)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_investment_template_with_missing_required_field_mapping(self):
        """Test validating an investment template with a missing required field mapping."""
        template = CSVTemplate(
            name="Test Investment Template",
            account_type=AccountType.INVESTMENT,
            field_mapping={
                "date": "Date",
                "action": "Action",
                "quantity": "Quantity",
                "price": "Price",
                "amount": "Amount"
            }
        )
        
        validator = TemplateValidator()
        
        is_valid, errors = validator.validate_template(template)
        
        assert is_valid is False
        assert len(errors) > 0
        assert any("security" in str(error).lower() for error in errors)
