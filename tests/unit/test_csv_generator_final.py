import pytest
from datetime import datetime
from unittest.mock import patch, mock_open

from quickenqifimport.generators.csv_generator import (
    CSVGenerator, CSVGeneratorError
)
from quickenqifimport.models.models import (
    AccountType, BankingTransaction, InvestmentTransaction, 
    InvestmentAction, SplitTransaction, ClearedStatus, CSVTemplate
)

class TestCSVGenerator:
    """Unit tests for CSV generator."""
    
    @pytest.fixture
    def bank_transactions(self):
        """Sample bank transactions."""
        return [
            BankingTransaction(
                date=datetime(2023, 1, 15),
                amount=-50.25,
                payee="Gas Station",
                memo="Fill up car",
                category="Auto:Fuel",
                number="123",
                cleared_status=ClearedStatus.CLEARED
            ),
            BankingTransaction(
                date=datetime(2023, 1, 16),
                amount=1200.00,
                payee="Paycheck",
                memo="January salary",
                category="Income:Salary",
                number="DIRECT DEP",
                cleared_status=ClearedStatus.RECONCILED
            ),
            BankingTransaction(
                date=datetime(2023, 1, 17),
                amount=-125.50,
                payee="Grocery Store",
                memo="Weekly groceries",
                category="Food:Groceries",
                splits=[
                    SplitTransaction(
                        category="Food:Groceries",
                        amount=-100.50,
                        memo="Groceries"
                    ),
                    SplitTransaction(
                        category="Household:Supplies",
                        amount=-25.00,
                        memo="Cleaning supplies"
                    )
                ]
            )
        ]
    
    @pytest.fixture
    def investment_transactions(self):
        """Sample investment transactions."""
        return [
            InvestmentTransaction(
                date=datetime(2023, 1, 15),
                action=InvestmentAction.BUY,
                security="AAPL",
                quantity=10,
                price=150.75,
                amount=-1507.50,
                commission=7.50,
                memo="Buy Apple stock",
                category="Investments:Stocks"
            ),
            InvestmentTransaction(
                date=datetime(2023, 1, 16),
                action=InvestmentAction.SELL,
                security="MSFT",
                quantity=5,
                price=250.25,
                amount=1251.25,
                commission=6.25,
                memo="Sell Microsoft stock",
                category="Investments:Stocks",
                cleared_status=ClearedStatus.CLEARED
            ),
            InvestmentTransaction(
                date=datetime(2023, 1, 17),
                action=InvestmentAction.DIV,
                security="VTI",
                amount=75.00,
                memo="Dividend payment",
                category="Income:Dividends"
            )
        ]
    
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
            date_format='%Y-%m-%d'
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
                'memo': 'Memo',
                'category': 'Category'
            },
            delimiter=',',
            has_header=True,
            date_format='%Y-%m-%d'
        )
    
    def test_init(self):
        """Test CSVGenerator initialization."""
        generator = CSVGenerator()
        assert generator is not None
    
    def test_generate_bank_csv(self, bank_transactions, bank_template):
        """Test generating CSV for bank transactions."""
        generator = CSVGenerator()
        
        csv_content = generator.generate_csv(bank_transactions, bank_template)
        
        assert "Date,Amount,Payee,Category,Memo,Number" in csv_content
        
        assert "2023-01-15,-50.25,Gas Station,Auto:Fuel,Fill up car,123" in csv_content
        assert "2023-01-16,1200.0,Paycheck,Income:Salary,January salary,DIRECT DEP" in csv_content
        assert "2023-01-17,-125.5,Grocery Store,Food:Groceries,Weekly groceries," in csv_content
    
    def test_generate_investment_csv(self, investment_transactions, investment_template):
        """Test generating CSV for investment transactions."""
        generator = CSVGenerator()
        
        csv_content = generator.generate_csv(investment_transactions, investment_template)
        
        assert "Date,Action,Security,Quantity,Price,Amount,Commission,Memo,Category" in csv_content
        
        assert "2023-01-15,Buy,AAPL,10,150.75,-1507.5,7.5,Buy Apple stock,Investments:Stocks" in csv_content
        assert "2023-01-16,Sell,MSFT,5,250.25,1251.25,6.25,Sell Microsoft stock,Investments:Stocks" in csv_content
        assert "2023-01-17,Div,VTI,,,75.0,,Dividend payment,Income:Dividends" in csv_content
    
    def test_generate_csv_file(self, bank_transactions, bank_template):
        """Test generating CSV file."""
        generator = CSVGenerator()
        
        mock = mock_open()
        with patch("builtins.open", mock):
            with patch("quickenqifimport.generators.csv_generator.CSVGenerator.generate_csv") as mock_generate:
                mock_generate.return_value = "CSV content"
                
                csv_content = generator.generate_csv(bank_transactions, bank_template)
                
                with open("/path/to/output.csv", "w", encoding="utf-8", newline="") as f:
                    f.write(csv_content)
                
                mock.assert_called_once_with("/path/to/output.csv", "w", encoding="utf-8", newline="")
    
    def test_generate_with_empty_transactions(self, bank_template):
        """Test generating CSV with empty transactions list."""
        generator = CSVGenerator()
        
        csv_content = generator.generate_csv([], bank_template)
        
        assert "Date,Amount,Payee,Category,Memo,Number" in csv_content
        assert csv_content.count('\n') == 1
    
    def test_generate_with_missing_fields(self, bank_transactions):
        """Test generating CSV with missing fields in template."""
        generator = CSVGenerator()
        
        template = CSVTemplate(
            name="missing_fields",
            account_type=AccountType.BANK,
            field_mapping={
                'date': 'Date',
                'amount': 'Amount'
            },
            delimiter=',',
            has_header=True
        )
        
        csv_content = generator.generate_csv(bank_transactions, template)
        
        assert "Date,Amount" in csv_content
        assert "2023-01-15,-50.25" in csv_content
        assert "Gas Station" not in csv_content
