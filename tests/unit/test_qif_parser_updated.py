import pytest
from datetime import datetime
from unittest.mock import patch, mock_open

from quickenqifimport.parsers.qif_parser import (
    QIFParser, QIFParserError
)
from quickenqifimport.models.models import (
    AccountType, BankingTransaction, InvestmentTransaction, 
    InvestmentAction, SplitTransaction, ClearedStatus, QIFFile
)

class TestQIFParser:
    """Unit tests for QIF parser."""
    
    @pytest.fixture
    def sample_bank_qif(self):
        """Sample bank QIF data."""
        return """!Type:Bank
D01/15/2023
T-50.25
PGas Station
MFill up car
LAuto:Fuel
N123
C*
^
D01/16/2023
T1200.00
PPaycheck
MJanuary salary
LIncome:Salary
NDIRECT DEP
CX
^
D01/17/2023
T-125.50
PGrocery Store
MWeekly groceries
LFood:Groceries
SFood:Groceries
EGroceries
$-100.50
SHousehold:Supplies
ECleaning supplies
$-25.00
^
"""
    
    @pytest.fixture
    def sample_investment_qif(self):
        """Sample investment QIF data."""
        return """!Type:Invst
D01/15/2023
NBuy
YAAPL
Q10
I150.75
T-1507.50
O7.50
MBuy Apple stock
LInvestments:Stocks
^
D01/16/2023
NSell
YMSFT
Q5
I250.25
T1251.25
O6.25
MSell Microsoft stock
LInvestments:Stocks
C*
^
D01/17/2023
NDiv
YVTI
T75.00
MDividend payment
LIncome:Dividends
^
"""
    
    @pytest.fixture
    def sample_qif_with_accounts(self):
        """Sample QIF data with account definitions."""
        return """!Account
NChecking
TBank
DPrimary checking account
^
NInvestment
TInvst
DInvestment account
^
!Type:Bank
D01/15/2023
T-50.25
PGas Station
MFill up car
LAuto:Fuel
N123
C*
^
!Type:Invst
D01/15/2023
NBuy
YAAPL
Q10
I150.75
T-1507.50
O7.50
MBuy Apple stock
LInvestments:Stocks
^
"""
    
    def test_init(self):
        """Test QIFParser initialization."""
        parser = QIFParser()
        assert parser is not None
    
    def test_parse_bank_qif(self, sample_bank_qif):
        """Test parsing bank QIF data."""
        parser = QIFParser()
        
        qif_file = parser.parse(sample_bank_qif)
            
        assert len(qif_file.bank_transactions.get('Default', [])) == 3
        
        transaction = qif_file.bank_transactions['Default'][0]
        assert transaction.date.strftime('%Y-%m-%d') == '2023-01-15'
        assert transaction.amount == -50.25
        assert transaction.payee == 'Gas Station'
        assert transaction.memo == 'Fill up car'
        assert transaction.category == 'Auto:Fuel'
        assert transaction.number == '123'
        assert transaction.cleared_status == ClearedStatus.CLEARED
        
        transaction = qif_file.bank_transactions['Default'][1]
        assert transaction.date.strftime('%Y-%m-%d') == '2023-01-16'
        assert transaction.amount == 1200.00
        assert transaction.payee == 'Paycheck'
        assert transaction.memo == 'January salary'
        assert transaction.category == 'Income:Salary'
        assert transaction.number == 'DIRECT DEP'
        assert transaction.cleared_status == ClearedStatus.RECONCILED
        
        transaction = qif_file.bank_transactions['Default'][2]
        assert transaction.date.strftime('%Y-%m-%d') == '2023-01-17'
        assert transaction.amount == -125.50
        assert transaction.payee == 'Grocery Store'
        assert transaction.memo == 'Weekly groceries'
        assert transaction.category == 'Food:Groceries'
        assert len(transaction.splits) == 2
        assert transaction.splits[0].category == 'Food:Groceries'
        assert transaction.splits[0].amount == -100.50
        assert transaction.splits[0].memo == 'Groceries'
        assert transaction.splits[1].category == 'Household:Supplies'
        assert transaction.splits[1].amount == -25.00
        assert transaction.splits[1].memo == 'Cleaning supplies'
    
    def test_parse_investment_qif(self, sample_investment_qif):
        """Test parsing investment QIF data."""
        parser = QIFParser()
        
        qif_file = parser.parse(sample_investment_qif)
        
        assert len(qif_file.investment_transactions.get('Default', [])) == 3
        
        transaction = qif_file.investment_transactions['Default'][0]
        assert transaction.date.strftime('%Y-%m-%d') == '2023-01-15'
        assert transaction.action == InvestmentAction.BUY
        assert transaction.security == 'AAPL'
        assert transaction.quantity == 10
        assert transaction.price == 150.75
        assert transaction.amount == -1507.50
        assert transaction.commission == 7.50
        assert transaction.memo == 'Buy Apple stock'
        assert transaction.category == 'Investments:Stocks'
        
        transaction = qif_file.investment_transactions['Default'][1]
        assert transaction.date.strftime('%Y-%m-%d') == '2023-01-16'
        assert transaction.action == InvestmentAction.SELL
        assert transaction.security == 'MSFT'
        assert transaction.quantity == 5
        assert transaction.price == 250.25
        assert transaction.amount == 1251.25
        assert transaction.commission == 6.25
        assert transaction.memo == 'Sell Microsoft stock'
        assert transaction.category == 'Investments:Stocks'
        assert transaction.cleared_status == ClearedStatus.CLEARED
        
        transaction = qif_file.investment_transactions['Default'][2]
        assert transaction.date.strftime('%Y-%m-%d') == '2023-01-17'
        assert transaction.action == InvestmentAction.DIV
        assert transaction.security == 'VTI'
        assert transaction.amount == 75.00
        assert transaction.memo == 'Dividend payment'
        assert transaction.category == 'Income:Dividends'
    
    def test_parse_qif_with_accounts(self, sample_qif_with_accounts):
        """Test parsing QIF data with account definitions."""
        parser = QIFParser()
        
        qif_file = parser.parse(sample_qif_with_accounts)
        
        assert len(qif_file.accounts) == 2
        
        account = qif_file.accounts[0]
        assert account.name == 'Checking'
        assert account.type == AccountType.BANK
        assert account.description == 'Primary checking account'
        
        account = qif_file.accounts[1]
        assert account.name == 'Investment'
        assert account.type == AccountType.INVESTMENT
        assert account.description == 'Investment account'
        
        assert len(qif_file.bank_transactions.get('Checking', [])) == 1
        
        assert len(qif_file.investment_transactions.get('Checking', [])) == 1
    
    def test_parse_empty_qif(self):
        """Test parsing empty QIF data."""
        parser = QIFParser()
        
        with pytest.raises(QIFParserError):
            parser.parse("")
    
    def test_parse_qif_with_invalid_date(self):
        """Test parsing QIF with invalid date."""
        parser = QIFParser()
        
        invalid_date_qif = """!Type:Bank
Dinvalid-date
T-50.25
^
"""
        
        with pytest.raises(QIFParserError):
            parser.parse(invalid_date_qif)
    
    def test_parse_qif_with_invalid_amount(self):
        """Test parsing QIF with invalid amount."""
        parser = QIFParser()
        
        invalid_amount_qif = """!Type:Bank
D01/15/2023
Tinvalid
^
"""
        
        with pytest.raises(QIFParserError):
            parser.parse(invalid_amount_qif)
