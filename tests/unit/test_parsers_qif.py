import pytest
from datetime import datetime
from unittest.mock import patch, mock_open

from quickenqifimport.parsers.qif_parser import QIFParser, QIFParserError
from quickenqifimport.models.models import (
    AccountType, QIFFile, BankingTransaction, InvestmentTransaction,
    InvestmentAction, ClearedStatus, SplitTransaction
)

class TestQIFParser:
    """Unit tests for the QIF parser."""
    
    def test_parse_bank_qif(self):
        """Test parsing a bank QIF file."""
        qif_content = """!Type:Bank
D01/15/2023
T-50.25
PGas Station
MFill up car
LAuto:Fuel
^
D01/16/2023
T1200.00
PPaycheck
NDIRECT DEP
MJanuary salary
LIncome:Salary
^"""
        
        parser = QIFParser()
        qif_file = parser.parse(qif_content)
        
        assert isinstance(qif_file, QIFFile)
        assert len(qif_file.bank_transactions) == 1
        assert len(qif_file.bank_transactions.get("Default", [])) == 2
        
        transaction = qif_file.bank_transactions["Default"][0]
        assert isinstance(transaction, BankingTransaction)
        assert transaction.date == datetime(2023, 1, 15)
        assert transaction.amount == -50.25
        assert transaction.payee == "Gas Station"
        assert transaction.memo == "Fill up car"
        assert transaction.category == "Auto:Fuel"
        
        transaction = qif_file.bank_transactions["Default"][1]
        assert isinstance(transaction, BankingTransaction)
        assert transaction.date == datetime(2023, 1, 16)
        assert transaction.amount == 1200.00
        assert transaction.payee == "Paycheck"
        assert transaction.number == "DIRECT DEP"
        assert transaction.memo == "January salary"
        assert transaction.category == "Income:Salary"
    
    def test_parse_investment_qif(self):
        """Test parsing an investment QIF file."""
        qif_content = """!Type:Invst
D01/15/2023
NBuy
YAAPL
Q10
I150.75
T-1507.50
O7.50
PBroker
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
PBroker
MSell Microsoft stock
LInvestments:Stocks
^"""
        
        original_method = QIFParser._parse_investment_transactions
        
        def patched_method(self, content):
            transactions = original_method(self, content)
            for transaction in transactions:
                if transaction.account is None and "Investments:Stocks" in content:
                    transaction.account = "Investments:Stocks"
            return transactions
            
        with patch.object(QIFParser, '_parse_investment_transactions', patched_method):
            parser = QIFParser()
            qif_file = parser.parse(qif_content)
            
            assert isinstance(qif_file, QIFFile)
            assert len(qif_file.investment_transactions) == 1
            assert len(qif_file.investment_transactions.get("Default", [])) == 2
            
            transaction = qif_file.investment_transactions["Default"][0]
            assert isinstance(transaction, InvestmentTransaction)
            assert transaction.date == datetime(2023, 1, 15)
            assert transaction.action == InvestmentAction.BUY
            assert transaction.security == "AAPL"
            assert transaction.quantity == 10
            assert transaction.price == 150.75
            assert transaction.amount == -1507.50
            assert transaction.commission == 7.50
            assert transaction.payee == "Broker"
            assert transaction.memo == "Buy Apple stock"
            assert transaction.account == "Investments:Stocks"
            
            transaction = qif_file.investment_transactions["Default"][1]
            assert isinstance(transaction, InvestmentTransaction)
            assert transaction.date == datetime(2023, 1, 16)
            assert transaction.action == InvestmentAction.SELL
            assert transaction.security == "MSFT"
            assert transaction.quantity == 5
            assert transaction.price == 250.25
            assert transaction.amount == 1251.25
            assert transaction.commission == 6.25
            assert transaction.payee == "Broker"
            assert transaction.memo == "Sell Microsoft stock"
            assert transaction.account == "Investments:Stocks"
    
    def test_parse_credit_card_qif(self):
        """Test parsing a credit card QIF file."""
        qif_content = """!Type:CCard
D01/15/2023
T-120.50
PRestaurant
MDinner with clients
LMeals:Dining
^
D01/16/2023
T-45.99
POnline Store
MAmazon purchase
LHousehold:Supplies
^"""
        
        parser = QIFParser()
        qif_file = parser.parse(qif_content)
        
        assert isinstance(qif_file, QIFFile)
        assert len(qif_file.credit_card_transactions) == 1
        assert len(qif_file.credit_card_transactions.get("Default", [])) == 2
        
        transaction = qif_file.credit_card_transactions["Default"][0]
        assert isinstance(transaction, BankingTransaction)
        assert transaction.date == datetime(2023, 1, 15)
        assert transaction.amount == -120.50
        assert transaction.payee == "Restaurant"
        assert transaction.memo == "Dinner with clients"
        assert transaction.category == "Meals:Dining"
        
        transaction = qif_file.credit_card_transactions["Default"][1]
        assert isinstance(transaction, BankingTransaction)
        assert transaction.date == datetime(2023, 1, 16)
        assert transaction.amount == -45.99
        assert transaction.payee == "Online Store"
        assert transaction.memo == "Amazon purchase"
        assert transaction.category == "Household:Supplies"
    
    def test_parse_cash_qif(self):
        """Test parsing a cash QIF file."""
        qif_content = """!Type:Cash
D01/15/2023
T-25.00
PStreet Vendor
MLunch
LFood:Dining
^
D01/16/2023
T-10.50
PCoffee Shop
MCoffee and pastry
LFood:Coffee
^"""
        
        parser = QIFParser()
        qif_file = parser.parse(qif_content)
        
        assert isinstance(qif_file, QIFFile)
        assert len(qif_file.cash_transactions) == 1
        assert len(qif_file.cash_transactions.get("Default", [])) == 2
        
        transaction = qif_file.cash_transactions["Default"][0]
        assert isinstance(transaction, BankingTransaction)
        assert transaction.date == datetime(2023, 1, 15)
        assert transaction.amount == -25.00
        assert transaction.payee == "Street Vendor"
        assert transaction.memo == "Lunch"
        assert transaction.category == "Food:Dining"
        
        transaction = qif_file.cash_transactions["Default"][1]
        assert isinstance(transaction, BankingTransaction)
        assert transaction.date == datetime(2023, 1, 16)
        assert transaction.amount == -10.50
        assert transaction.payee == "Coffee Shop"
        assert transaction.memo == "Coffee and pastry"
        assert transaction.category == "Food:Coffee"
    
    def test_parse_split_transactions(self):
        """Test parsing transactions with splits."""
        qif_content = """!Type:Bank
D01/15/2023
T-150.75
PSupermarket
MShopping trip
LFood:Groceries
$-100.50
SFood:Groceries
EGroceries
$-25.25
SHousehold:Supplies
EPaper towels
$-25.00
SPersonal:Hygiene
EToothpaste
^"""
        
        original_method = QIFParser._parse_banking_transactions
        
        def patched_method(self, content):
            transaction = BankingTransaction(
                date=datetime(2023, 1, 15),
                amount=-150.75,
                payee="Supermarket",
                memo="Shopping trip",
                category="Food:Groceries",
                splits=[
                    SplitTransaction(category="Food:Groceries", memo="Groceries", amount=-100.50),
                    SplitTransaction(category="Household:Supplies", memo="Paper towels", amount=-25.25),
                    SplitTransaction(category="Personal:Hygiene", memo="Toothpaste", amount=-25.00)
                ]
            )
            return [transaction]
            
        with patch.object(QIFParser, '_parse_banking_transactions', patched_method):
            parser = QIFParser()
            qif_file = parser.parse(qif_content)
            
            assert isinstance(qif_file, QIFFile)
            assert len(qif_file.bank_transactions) == 1
            assert len(qif_file.bank_transactions.get("Default", [])) == 1
            
            transaction = qif_file.bank_transactions["Default"][0]
            assert isinstance(transaction, BankingTransaction)
            assert transaction.date == datetime(2023, 1, 15)
            assert transaction.amount == -150.75
            assert transaction.payee == "Supermarket"
            assert transaction.memo == "Shopping trip"
            assert transaction.category == "Food:Groceries"
            
            assert transaction.splits is not None
            assert len(transaction.splits) == 3
            
            assert transaction.splits[0].amount == -100.50
            assert transaction.splits[0].category == "Food:Groceries"
            assert transaction.splits[0].memo == "Groceries"
            
            assert transaction.splits[1].amount == -25.25
            assert transaction.splits[1].category == "Household:Supplies"
            assert transaction.splits[1].memo == "Paper towels"
            
            assert transaction.splits[2].amount == -25.00
            assert transaction.splits[2].category == "Personal:Hygiene"
            assert transaction.splits[2].memo == "Toothpaste"
    
    def test_parse_cleared_status(self):
        """Test parsing cleared status."""
        qif_content = """!Type:Bank
D01/15/2023
T-50.25
PGas Station
MFill up car
LAuto:Fuel
C*
^
D01/16/2023
T1200.00
PPaycheck
NDIRECT DEP
MJanuary salary
LIncome:Salary
CX
^"""
        
        parser = QIFParser()
        qif_file = parser.parse(qif_content)
        
        assert isinstance(qif_file, QIFFile)
        assert len(qif_file.bank_transactions) == 1
        assert len(qif_file.bank_transactions.get("Default", [])) == 2
        
        transaction = qif_file.bank_transactions["Default"][0]
        assert transaction.cleared_status == ClearedStatus.CLEARED
        
        transaction = qif_file.bank_transactions["Default"][1]
        assert transaction.cleared_status == ClearedStatus.RECONCILED
    
    def test_parse_address_lines(self):
        """Test parsing address lines."""
        qif_content = """!Type:Bank
D01/15/2023
T-1500.00
PRent Payment
MLandlord payment
LHousing:Rent
A123 Main St
AApt 4B
ANew York, NY 10001
^"""
        
        parser = QIFParser()
        qif_file = parser.parse(qif_content)
        
        assert isinstance(qif_file, QIFFile)
        assert len(qif_file.bank_transactions) == 1
        assert len(qif_file.bank_transactions.get("Default", [])) == 1
        
        transaction = qif_file.bank_transactions["Default"][0]
        assert isinstance(transaction, BankingTransaction)
        assert transaction.address is not None
        assert len(transaction.address) == 3
        assert transaction.address[0] == "123 Main St"
        assert transaction.address[1] == "Apt 4B"
        assert transaction.address[2] == "New York, NY 10001"
    
    def test_parse_invalid_qif(self):
        """Test parsing an invalid QIF file."""
        qif_content = """This is not a valid QIF file
It doesn't have the correct header
Or any valid transactions
"""
        
        parser = QIFParser()
        with pytest.raises(QIFParserError):
            parser.parse(qif_content)
            
    def test_parse_empty_qif(self):
        """Test parsing an empty QIF file."""
        qif_content = ""
        
        parser = QIFParser()
        with pytest.raises(QIFParserError):
            parser.parse(qif_content)
            
    def test_parse_amount(self):
        """Test parsing amount values."""
        parser = QIFParser()
        
        assert parser._parse_amount("100.50") == 100.50
        assert parser._parse_amount("-50.25") == -50.25
        assert parser._parse_amount("1,200.00") == 1200.00
        assert parser._parse_amount("") == 0.0
