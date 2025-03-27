import pytest
from datetime import datetime
from unittest.mock import patch, mock_open

from quickenqifimport.generators.qif_generator import (
    QIFGenerator, generate_qif_file, QIFGeneratorError
)
from quickenqifimport.models.models import (
    AccountType, BankingTransaction, InvestmentTransaction, 
    InvestmentAction, SplitTransaction, ClearedStatus
)

class TestQIFGenerator:
    """Unit tests for QIF generator."""
    
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
    
    def test_init(self):
        """Test QIFGenerator initialization."""
        generator = QIFGenerator()
        assert generator is not None
    
    def test_generate_bank_qif(self, bank_transactions):
        """Test generating QIF for bank transactions."""
        generator = QIFGenerator()
        
        qif_content = generator.generate(bank_transactions, AccountType.BANK)
        
        assert qif_content.startswith("!Type:Bank")
        
        assert "D01/15/2023" in qif_content
        assert "T-50.25" in qif_content
        assert "PGas Station" in qif_content
        assert "MFill up car" in qif_content
        assert "LAuto:Fuel" in qif_content
        assert "N123" in qif_content
        assert "C*" in qif_content  # Cleared status
        
        assert "D01/16/2023" in qif_content
        assert "T1200.00" in qif_content
        assert "PPaycheck" in qif_content
        assert "MJanuary salary" in qif_content
        assert "LIncome:Salary" in qif_content
        assert "NDIRECT DEP" in qif_content
        assert "CX" in qif_content  # Reconciled status
        
        assert "D01/17/2023" in qif_content
        assert "T-125.50" in qif_content
        assert "PGrocery Store" in qif_content
        assert "MWeekly groceries" in qif_content
        assert "SFood:Groceries" in qif_content
        assert "E-100.50" in qif_content
        assert "SHousehold:Supplies" in qif_content
        assert "E-25.00" in qif_content
    
    def test_generate_investment_qif(self, investment_transactions):
        """Test generating QIF for investment transactions."""
        generator = QIFGenerator()
        
        qif_content = generator.generate(investment_transactions, AccountType.INVESTMENT)
        
        assert qif_content.startswith("!Type:Invst")
        
        assert "D01/15/2023" in qif_content
        assert "NBuy" in qif_content
        assert "YAAPL" in qif_content
        assert "Q10" in qif_content
        assert "I150.75" in qif_content
        assert "T-1507.50" in qif_content
        assert "O7.50" in qif_content
        assert "MBuy Apple stock" in qif_content
        assert "LInvestments:Stocks" in qif_content
        
        assert "D01/16/2023" in qif_content
        assert "NSell" in qif_content
        assert "YMSFT" in qif_content
        assert "Q5" in qif_content
        assert "I250.25" in qif_content
        assert "T1251.25" in qif_content
        assert "O6.25" in qif_content
        assert "MSell Microsoft stock" in qif_content
        assert "C*" in qif_content  # Cleared status
        
        assert "D01/17/2023" in qif_content
        assert "NDiv" in qif_content
        assert "YVTI" in qif_content
        assert "T75.00" in qif_content
        assert "MDividend payment" in qif_content
        assert "LIncome:Dividends" in qif_content
    
    def test_generate_qif_file_function(self, bank_transactions):
        """Test the generate_qif_file function."""
        mock = mock_open()
        with patch("builtins.open", mock):
            generate_qif_file(
                bank_transactions,
                AccountType.BANK,
                "/path/to/output.qif"
            )
            
            mock.assert_called_once_with("/path/to/output.qif", "w", encoding="utf-8")
            
            written_data = mock().write.call_args[0][0]
            assert written_data.startswith("!Type:Bank")
    
    def test_generate_with_invalid_account_type(self, bank_transactions):
        """Test generating QIF with invalid account type."""
        generator = QIFGenerator()
        
        with pytest.raises(QIFGeneratorError):
            generator.generate(bank_transactions, "InvalidType")
    
    def test_generate_with_empty_transactions(self):
        """Test generating QIF with empty transactions list."""
        generator = QIFGenerator()
        
        with pytest.raises(QIFGeneratorError):
            generator.generate([], AccountType.BANK)
