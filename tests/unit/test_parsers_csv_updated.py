import pytest
from unittest.mock import patch, mock_open
import pandas as pd
from io import StringIO

from quickenqifimport.parsers.csv_parser import (
    CSVParser, CSVParserError
)
from quickenqifimport.models.models import (
    AccountType, BankingTransaction, InvestmentTransaction, InvestmentAction,
    CSVTemplate
)

class TestCSVParser:
    """Unit tests for CSV parser."""
    
    @pytest.fixture
    def sample_bank_csv(self):
        """Sample bank CSV data."""
        return """Date,Amount,Payee,Category,Memo,Number
2023-01-15,-50.25,Gas Station,Auto:Fuel,Fill up car,123
2023-01-16,1200.00,Paycheck,Income:Salary,January salary,DIRECT DEP
2023-01-17,-125.50,Grocery Store,Food:Groceries,Weekly groceries,
"""
    
    @pytest.fixture
    def sample_investment_csv(self):
        """Sample investment CSV data."""
        return """Date,Action,Security,Quantity,Price,Amount,Commission,Memo
2023-01-15,Buy,AAPL,10,150.75,-1507.50,7.50,Buy Apple stock
2023-01-16,Sell,MSFT,5,250.25,1251.25,6.25,Sell Microsoft stock
2023-01-17,Div,VTI,,,75.00,,Dividend payment
"""
    
    @pytest.fixture
    def bank_template(self):
        """Bank CSV template."""
        return CSVTemplate(
            name="test_bank",
            account_type=AccountType.BANK,
            field_mapping={
                'date': 'Date',
                'amount': 'Amount',
                'payee': 'Payee',
                'category': 'Category',
                'memo': 'Memo',
                'number': 'Number'
            },
            delimiter=',',
            has_header=True,
            skip_rows=0
        )
    
    @pytest.fixture
    def investment_template(self):
        """Investment CSV template."""
        return CSVTemplate(
            name="test_investment",
            account_type=AccountType.INVESTMENT,
            field_mapping={
                'date': 'Date',
                'action': 'Action',
                'security': 'Security',
                'quantity': 'Quantity',
                'price': 'Price',
                'amount': 'Amount',
                'commission': 'Commission',
                'memo': 'Memo'
            },
            delimiter=',',
            has_header=True,
            skip_rows=0
        )
    
    def test_init(self):
        """Test CSVParser initialization."""
        parser = CSVParser()
        assert parser._transaction_classes[AccountType.BANK] == BankingTransaction
        assert parser._transaction_classes[AccountType.INVESTMENT] == InvestmentTransaction
        assert 'date' in parser._field_handlers
        assert 'amount' in parser._field_handlers
        assert 'action' in parser._field_handlers
    
    def test_parse_csv_bank(self, sample_bank_csv, bank_template):
        """Test parsing bank CSV data."""
        parser = CSVParser()
        
        transactions = parser.parse_csv(sample_bank_csv, bank_template)
        
        assert len(transactions) == 3
        
        assert transactions[0].date.strftime('%Y-%m-%d') == '2023-01-15'
        assert transactions[0].amount == -50.25
        assert transactions[0].payee == 'Gas Station'
        assert transactions[0].category == 'Auto:Fuel'
        assert transactions[0].memo == 'Fill up car'
        assert transactions[0].number == '123'
        
        assert transactions[1].date.strftime('%Y-%m-%d') == '2023-01-16'
        assert transactions[1].amount == 1200.00
        assert transactions[1].payee == 'Paycheck'
        assert transactions[1].category == 'Income:Salary'
        assert transactions[1].memo == 'January salary'
        assert transactions[1].number == 'DIRECT DEP'
    
    def test_parse_csv_investment(self, sample_investment_csv, investment_template):
        """Test parsing investment CSV data."""
        parser = CSVParser()
        
        transactions = parser.parse_csv(sample_investment_csv, investment_template)
        
        assert len(transactions) == 3
        
        assert transactions[0].date.strftime('%Y-%m-%d') == '2023-01-15'
        assert transactions[0].action == 'Buy'  # String representation
        assert transactions[0].security == 'AAPL'
        assert transactions[0].quantity == 10
        assert transactions[0].price == 150.75
        assert transactions[0].amount == -1507.50
        assert transactions[0].commission == 7.50
        assert transactions[0].memo == 'Buy Apple stock'
        
        assert transactions[1].date.strftime('%Y-%m-%d') == '2023-01-16'
        assert transactions[1].action == 'Sell'  # String representation
        assert transactions[1].security == 'MSFT'
        assert transactions[1].quantity == 5
        assert transactions[1].price == 250.25
        assert transactions[1].amount == 1251.25
        assert transactions[1].commission == 6.25
        assert transactions[1].memo == 'Sell Microsoft stock'
        
        assert transactions[2].date.strftime('%Y-%m-%d') == '2023-01-17'
        assert transactions[2].action == 'Div'  # String representation
        assert transactions[2].security == 'VTI'
        assert transactions[2].amount == 75.00
        assert transactions[2].memo == 'Dividend payment'
    
    def test_parse_csv_empty(self, bank_template):
        """Test parsing empty CSV."""
        parser = CSVParser()
        
        transactions = parser.parse_csv("", bank_template)
        
        assert len(transactions) == 0
    
    def test_parse_csv_missing_required_field(self, sample_bank_csv):
        """Test parsing CSV with missing required fields."""
        parser = CSVParser()
        
        template = CSVTemplate(
            name="missing_date",
            account_type=AccountType.BANK,
            field_mapping={
                'amount': 'Amount',
                'payee': 'Payee',
                'category': 'Category'
            },
            delimiter=',',
            has_header=True,
            skip_rows=0
        )
        
        with pytest.raises(CSVParserError):
            parser.parse_csv(sample_bank_csv, template)
    
    def test_parse_csv_invalid_data(self):
        """Test parsing CSV with invalid data."""
        parser = CSVParser()
        
        invalid_csv = """Date,Amount,Payee
2023-01-15,invalid,Gas Station
"""
        
        template = CSVTemplate(
            name="test_bank",
            account_type=AccountType.BANK,
            field_mapping={
                'date': 'Date',
                'amount': 'Amount',
                'payee': 'Payee'
            },
            delimiter=',',
            has_header=True,
            skip_rows=0
        )
        
        with pytest.raises(CSVParserError):
            parser.parse_csv(invalid_csv, template)
    
    def test_handle_amount(self):
        """Test handling amount field with different formats."""
        parser = CSVParser()
        template = CSVTemplate(
            name="test_bank",
            account_type=AccountType.BANK,
            field_mapping={},
            delimiter=',',
            has_header=True,
            skip_rows=0
        )
        
        assert parser._handle_amount("123.45", "amount", template, [], None, 1) == 123.45
        
        assert parser._handle_amount("-123.45", "amount", template, [], None, 1) == -123.45
        
        assert parser._handle_amount("$123.45", "amount", template, [], None, 1) == 123.45
        
        assert parser._handle_amount("1,234.56", "amount", template, [], None, 1) == 1234.56
        
        assert parser._handle_amount("123,45", "amount", template, [], None, 1) == 123.45
        
        template.amount_multiplier = {"amount": -1}
        assert parser._handle_amount("123.45", "amount", template, [], None, 1) == -123.45
        
        with pytest.raises(CSVParserError):
            parser._handle_amount("invalid", "amount", template, [], None, 1)
    
    def test_handle_date(self):
        """Test handling date field with different formats."""
        parser = CSVParser()
        template = CSVTemplate(
            name="test_bank",
            account_type=AccountType.BANK,
            field_mapping={},
            delimiter=',',
            has_header=True,
            skip_rows=0
        )
        
        date = parser._handle_date("2023-01-15", "date", template, [], None, 1)
        assert date.strftime('%Y-%m-%d') == '2023-01-15'
        
        date = parser._handle_date("01/15/2023", "date", template, [], None, 1)
        assert date.strftime('%Y-%m-%d') == '2023-01-15'
        
        template.date_format = "%d.%m.%Y"
        date = parser._handle_date("15.01.2023", "date", template, [], None, 1)
        assert date.strftime('%Y-%m-%d') == '2023-01-15'
        
        with pytest.raises(CSVParserError):
            parser._handle_date("invalid", "date", template, [], None, 1)
    
    def test_handle_investment_action(self):
        """Test handling investment action field."""
        parser = CSVParser()
        template = CSVTemplate(
            name="test_investment",
            account_type=AccountType.INVESTMENT,
            field_mapping={},
            delimiter=',',
            has_header=True,
            skip_rows=0
        )
        
        assert parser._handle_investment_action("Buy", "action", template, [], None, 1) == "Buy"
        assert parser._handle_investment_action("Sell", "action", template, [], None, 1) == "Sell"
        assert parser._handle_investment_action("Div", "action", template, [], None, 1) == "Div"
        
        assert parser._handle_investment_action("buy", "action", template, [], None, 1) == "Buy"
        assert parser._handle_investment_action("sell", "action", template, [], None, 1) == "Sell"
        assert parser._handle_investment_action("div", "action", template, [], None, 1) == "Div"
        
        assert parser._handle_investment_action("dividend", "action", template, [], None, 1) == "Div"
        assert parser._handle_investment_action("reinvest", "action", template, [], None, 1) == "ReinvDiv"
        assert parser._handle_investment_action("interest", "action", template, [], None, 1) == "IntInc"
