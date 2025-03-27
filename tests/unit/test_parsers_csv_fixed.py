import pytest
from unittest.mock import patch, mock_open
import pandas as pd
from io import StringIO

from quickenqifimport.parsers.csv_parser import (
    CSVParser, CSVParserError, parse_csv_to_transactions
)
from quickenqifimport.models.models import (
    AccountType, BankingTransaction, InvestmentTransaction, InvestmentAction
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
    
    def test_init(self):
        """Test CSVParser initialization."""
        parser = CSVParser()
        assert parser.delimiter == ','
        assert parser.has_header is True
        assert parser.skip_rows == 0
        
        parser = CSVParser(delimiter=';', has_header=False, skip_rows=2)
        assert parser.delimiter == ';'
        assert parser.has_header is False
        assert parser.skip_rows == 2
    
    def test_parse_bank_csv(self, sample_bank_csv):
        """Test parsing bank CSV data."""
        with patch('builtins.open', mock_open(read_data=sample_bank_csv)):
            parser = CSVParser()
            
            field_mapping = {
                'date': 'Date',
                'amount': 'Amount',
                'payee': 'Payee',
                'category': 'Category',
                'memo': 'Memo',
                'number': 'Number'
            }
            
            transactions = parser.parse('/path/to/file.csv', AccountType.BANK, field_mapping)
            
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
    
    def test_parse_investment_csv(self, sample_investment_csv):
        """Test parsing investment CSV data."""
        with patch('builtins.open', mock_open(read_data=sample_investment_csv)):
            parser = CSVParser()
            
            field_mapping = {
                'date': 'Date',
                'action': 'Action',
                'security': 'Security',
                'quantity': 'Quantity',
                'price': 'Price',
                'amount': 'Amount',
                'commission': 'Commission',
                'memo': 'Memo'
            }
            
            transactions = parser.parse('/path/to/file.csv', AccountType.INVESTMENT, field_mapping)
            
            assert len(transactions) == 3
            
            assert transactions[0].date.strftime('%Y-%m-%d') == '2023-01-15'
            assert transactions[0].action == InvestmentAction.BUY
            assert transactions[0].security == 'AAPL'
            assert transactions[0].quantity == 10
            assert transactions[0].price == 150.75
            assert transactions[0].amount == -1507.50
            assert transactions[0].commission == 7.50
            assert transactions[0].memo == 'Buy Apple stock'
            
            assert transactions[1].date.strftime('%Y-%m-%d') == '2023-01-16'
            assert transactions[1].action == InvestmentAction.SELL
            assert transactions[1].security == 'MSFT'
            assert transactions[1].quantity == 5
            assert transactions[1].price == 250.25
            assert transactions[1].amount == 1251.25
            assert transactions[1].commission == 6.25
            assert transactions[1].memo == 'Sell Microsoft stock'
            
            assert transactions[2].date.strftime('%Y-%m-%d') == '2023-01-17'
            assert transactions[2].action == InvestmentAction.DIV
            assert transactions[2].security == 'VTI'
            assert transactions[2].quantity is None
            assert transactions[2].price is None
            assert transactions[2].amount == 75.00
            assert transactions[2].commission is None
            assert transactions[2].memo == 'Dividend payment'
    
    def test_parse_csv_with_missing_required_fields(self, sample_bank_csv):
        """Test parsing CSV with missing required fields."""
        with patch('builtins.open', mock_open(read_data=sample_bank_csv)):
            parser = CSVParser()
            
            field_mapping = {
                'amount': 'Amount',
                'payee': 'Payee',
                'category': 'Category'
            }
            
            with pytest.raises(CSVParserError):
                parser.parse('/path/to/file.csv', AccountType.BANK, field_mapping)
    
    def test_parse_csv_with_invalid_data(self):
        """Test parsing CSV with invalid data."""
        invalid_csv = """Date,Amount,Payee
2023-01-15,invalid,Gas Station
"""
        
        with patch('builtins.open', mock_open(read_data=invalid_csv)):
            parser = CSVParser()
            
            field_mapping = {
                'date': 'Date',
                'amount': 'Amount',
                'payee': 'Payee'
            }
            
            with pytest.raises(CSVParserError):
                parser.parse('/path/to/file.csv', AccountType.BANK, field_mapping)
    
    def test_parse_csv_to_transactions_function(self, sample_bank_csv):
        """Test the parse_csv_to_transactions function."""
        with patch('builtins.open', mock_open(read_data=sample_bank_csv)):
            field_mapping = {
                'date': 'Date',
                'amount': 'Amount',
                'payee': 'Payee',
                'category': 'Category',
                'memo': 'Memo',
                'number': 'Number'
            }
            
            transactions = parse_csv_to_transactions(
                '/path/to/file.csv',
                AccountType.BANK,
                field_mapping
            )
            
            assert len(transactions) == 3
            assert isinstance(transactions[0], BankingTransaction)
            assert transactions[0].payee == 'Gas Station'
