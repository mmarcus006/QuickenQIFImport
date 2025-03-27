import pytest
from datetime import datetime
from unittest.mock import patch, mock_open

from quickenqifimport.generators.qif_generator import (
    QIFGenerator, QIFGeneratorError
)
from quickenqifimport.models.models import (
    AccountType, BankingTransaction, InvestmentTransaction, 
    InvestmentAction, SplitTransaction, ClearedStatus, QIFFile,
    AccountDefinition, CategoryItem, ClassItem, MemorizedTransaction,
    MemorizedTransactionType
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
    
    @pytest.fixture
    def qif_file(self, bank_transactions, investment_transactions):
        """Sample QIF file model."""
        return QIFFile(
            accounts=[
                AccountDefinition(
                    name="Checking",
                    type=AccountType.BANK,
                    description="Primary checking account"
                ),
                AccountDefinition(
                    name="Investment",
                    type=AccountType.INVESTMENT,
                    description="Investment account"
                )
            ],
            bank_transactions={"Checking": bank_transactions},
            investment_transactions={"Investment": investment_transactions},
            categories=[
                CategoryItem(
                    name="Auto:Fuel",
                    description="Gasoline and fuel expenses",
                    expense=True
                ),
                CategoryItem(
                    name="Income:Salary",
                    description="Employment income",
                    income=True
                )
            ]
        )
    
    def test_init(self):
        """Test QIFGenerator initialization."""
        generator = QIFGenerator()
        assert generator.date_format == '%m/%d/%Y'
        
        generator = QIFGenerator(date_format='%Y-%m-%d')
        assert generator.date_format == '%Y-%m-%d'
    
    def test_get_enum_value(self):
        """Test getting enum values."""
        generator = QIFGenerator()
        
        assert generator._get_enum_value("Test") == "Test"
        
        assert generator._get_enum_value(InvestmentAction.BUY) == "Buy"
        assert generator._get_enum_value(InvestmentAction.SELL) == "Sell"
        assert generator._get_enum_value(InvestmentAction.DIV) == "Div"
    
    def test_generate_qif(self, bank_transactions):
        """Test generating QIF for bank transactions."""
        generator = QIFGenerator()
        
        qif_content = generator.generate_qif(bank_transactions, AccountType.BANK, "Checking")
        
        assert qif_content.startswith("!Type:Bank")
        
        assert "D01/15/2023" in qif_content
        assert "T-50.25" in qif_content
        assert "PGas Station" in qif_content
        assert "MFill up car" in qif_content
        assert "LAuto:Fuel" in qif_content
        assert "N123" in qif_content
        
        assert "C" in qif_content
        
        assert "D01/16/2023" in qif_content
        assert "T1200.00" in qif_content
        assert "PPaycheck" in qif_content
        assert "MJanuary salary" in qif_content
        assert "LIncome:Salary" in qif_content
        assert "NDIRECT DEP" in qif_content
        
        assert "D01/17/2023" in qif_content
        assert "T-125.50" in qif_content
        assert "PGrocery Store" in qif_content
        assert "MWeekly groceries" in qif_content
        assert "SFood:Groceries" in qif_content
        assert "$-100.50" in qif_content
        assert "SHousehold:Supplies" in qif_content
        assert "$-25.00" in qif_content
    
    def test_generate_qif_with_account_info(self, bank_transactions):
        """Test generating QIF with account information."""
        generator = QIFGenerator()
        
        qif_content = generator.generate_qif(
            bank_transactions, 
            AccountType.BANK, 
            "Checking",
            include_account_info=True
        )
        
        assert "!Account" in qif_content
        assert "NChecking" in qif_content
        assert "TBank" in qif_content
        
        assert "!Type:Bank" in qif_content
    
    def test_generate_qif_investment(self, investment_transactions):
        """Test generating QIF for investment transactions."""
        generator = QIFGenerator()
        
        qif_content = generator.generate_qif(
            investment_transactions, 
            AccountType.INVESTMENT, 
            "Investment"
        )
        
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
        
        assert "C" in qif_content
        
        assert "D01/17/2023" in qif_content
        assert "NDiv" in qif_content
        assert "YVTI" in qif_content
        assert "T75.00" in qif_content
        assert "MDividend payment" in qif_content
        assert "LIncome:Dividends" in qif_content
    
    def test_generate_qif_file(self, qif_file):
        """Test generating QIF from a QIFFile model."""
        generator = QIFGenerator()
        
        qif_content = generator.generate_qif_file(qif_file)
        
        assert "!Account" in qif_content
        assert "NChecking" in qif_content
        assert "TBank" in qif_content
        assert "NPrimary checking account" in qif_content or "DPrimary checking account" in qif_content
        assert "NInvestment" in qif_content
        assert "TInvst" in qif_content
        
        assert "!Type:Bank" in qif_content
        assert "D01/15/2023" in qif_content
        assert "T-50.25" in qif_content
        assert "PGas Station" in qif_content
        
        assert "!Type:Invst" in qif_content
        assert "NBuy" in qif_content
        assert "YAAPL" in qif_content
        
        assert "!Type:Cat" in qif_content
        assert "NAuto:Fuel" in qif_content
        assert "E" in qif_content  # Expense flag
        assert "NIncome:Salary" in qif_content
        assert "I" in qif_content  # Income flag
    
    def test_generate_with_invalid_account_type(self, bank_transactions):
        """Test generating QIF with invalid account type."""
        generator = QIFGenerator()
        
        with pytest.raises(QIFGeneratorError):
            generator.generate_qif(bank_transactions, "InvalidType", "Checking")
    
    def test_generate_with_mismatched_transaction_type(self, bank_transactions, investment_transactions):
        """Test generating QIF with mismatched transaction and account types."""
        generator = QIFGenerator()
        
        with pytest.raises(QIFGeneratorError):
            generator.generate_qif(bank_transactions, AccountType.INVESTMENT, "Investment")
        
        with pytest.raises(QIFGeneratorError):
            generator.generate_qif(investment_transactions, AccountType.BANK, "Checking")
