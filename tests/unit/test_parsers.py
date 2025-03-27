import pytest
from datetime import datetime
import io
import csv

from quickenqifimport.parsers.csv_parser import CSVParser, CSVParserError
from quickenqifimport.parsers.qif_parser import QIFParser, QIFParserError
from quickenqifimport.models.models import (
    CSVTemplate, AccountType, BankingTransaction, InvestmentTransaction,
    QIFFile
)

class TestCSVParser:
    """Tests for the CSVParser class."""
    
    def test_parse_banking_csv(self):
        """Test parsing a banking CSV file."""
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
        
        parser = CSVParser()
        
        transactions = parser.parse_csv(csv_content, template)
        
        assert len(transactions) == 3
        
        assert isinstance(transactions[0], BankingTransaction)
        assert transactions[0].date == datetime(2023, 1, 1)
        assert transactions[0].amount == 100.50
        assert transactions[0].payee == "Grocery Store"
        assert transactions[0].number == "123"
        assert transactions[0].memo == "Weekly groceries"
        assert transactions[0].category == "Food:Groceries"
        
        assert transactions[1].amount == -50.25
        assert transactions[1].payee == "Gas Station"
        assert transactions[1].number is None  # Empty field
        
        assert transactions[2].amount == 1200.00
        assert transactions[2].payee == "Paycheck"
        assert transactions[2].number == "DIRECT DEP"
    
    def test_parse_investment_csv(self):
        """Test parsing an investment CSV file."""
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
        
        parser = CSVParser()
        
        transactions = parser.parse_csv(csv_content, template)
        
        assert len(transactions) == 3
        
        assert isinstance(transactions[0], InvestmentTransaction)
        assert transactions[0].date == datetime(2023, 1, 1)
        assert transactions[0].action == "Buy"
        assert transactions[0].security == "AAPL"
        assert transactions[0].quantity == 10
        assert transactions[0].price == 150.75
        assert transactions[0].amount == -1507.50
        assert transactions[0].commission == 7.50
        assert transactions[0].payee == "Broker"
        assert transactions[0].memo == "Buy Apple stock"
        assert transactions[0].category == "Investments:Stocks"
        
        assert transactions[1].action == "Sell"
        assert transactions[1].security == "MSFT"
        assert transactions[1].quantity == 5
        
        assert transactions[2].action == "Div"
        assert transactions[2].security == "VTI"
        assert transactions[2].quantity is None  # Empty field
        assert transactions[2].price is None  # Empty field
    
    def test_parse_csv_with_custom_delimiter(self):
        """Test parsing a CSV file with a custom delimiter."""
        csv_content = """Date;Amount;Description;Notes
2023-01-01;100.50;Grocery Store;Weekly groceries
2023-01-02;-50.25;Gas Station;Fill up car
"""
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            delimiter=";",
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description",
                "memo": "Notes"
            },
            date_format="%Y-%m-%d"
        )
        
        parser = CSVParser()
        
        transactions = parser.parse_csv(csv_content, template)
        
        assert len(transactions) == 2
        
        assert transactions[0].date == datetime(2023, 1, 1)
        assert transactions[0].amount == 100.50
        assert transactions[0].payee == "Grocery Store"
        assert transactions[0].memo == "Weekly groceries"
    
    def test_parse_csv_with_skip_rows(self):
        """Test parsing a CSV file with skipping rows."""
        csv_content = """This is a header row that should be skipped
This is another row to skip
Date,Amount,Description,Notes
2023-01-01,100.50,Grocery Store,Weekly groceries
2023-01-02,-50.25,Gas Station,Fill up car
"""
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            skip_rows=2,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description",
                "memo": "Notes"
            },
            date_format="%Y-%m-%d"
        )
        
        parser = CSVParser()
        
        transactions = parser.parse_csv(csv_content, template)
        
        assert len(transactions) == 2
        
        assert transactions[0].date == datetime(2023, 1, 1)
        assert transactions[0].amount == 100.50
        assert transactions[0].payee == "Grocery Store"
        assert transactions[0].memo == "Weekly groceries"
    
    def test_parse_csv_without_header(self):
        """Test parsing a CSV file without a header."""
        csv_content = """2023-01-01,100.50,Grocery Store,Weekly groceries
2023-01-02,-50.25,Gas Station,Fill up car
"""
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            has_header=False,
            field_mapping={
                "date": "0",
                "amount": "1",
                "payee": "2",
                "memo": "3"
            },
            date_format="%Y-%m-%d"
        )
        
        parser = CSVParser()
        
        transactions = parser.parse_csv(csv_content, template)
        
        assert len(transactions) == 2
        
        assert transactions[0].date == datetime(2023, 1, 1)
        assert transactions[0].amount == 100.50
        assert transactions[0].payee == "Grocery Store"
        assert transactions[0].memo == "Weekly groceries"
    
    def test_parse_csv_with_different_date_format(self):
        """Test parsing a CSV file with a different date format."""
        csv_content = """Date,Amount,Description
01/15/2023,100.50,Grocery Store
02/28/2023,-50.25,Gas Station
"""
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description"
            },
            date_format="%m/%d/%Y"
        )
        
        parser = CSVParser()
        
        transactions = parser.parse_csv(csv_content, template)
        
        assert len(transactions) == 2
        
        assert transactions[0].date == datetime(2023, 1, 15)
        
        assert transactions[1].date == datetime(2023, 2, 28)
    
    def test_parse_csv_with_missing_required_field(self):
        """Test parsing a CSV file with a missing required field."""
        csv_content = """Date,Description,Notes
2023-01-01,Grocery Store,Weekly groceries
2023-01-02,Gas Station,Fill up car
"""
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",  # This field is missing in the CSV
                "payee": "Description",
                "memo": "Notes"
            },
            date_format="%Y-%m-%d"
        )
        
        parser = CSVParser()
        
        with pytest.raises(CSVParserError):
            parser.parse_csv(csv_content, template)
    
    def test_parse_csv_with_invalid_date(self):
        """Test parsing a CSV file with an invalid date."""
        csv_content = """Date,Amount,Description
invalid-date,100.50,Grocery Store
2023-01-02,-50.25,Gas Station
"""
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description"
            },
            date_format="%Y-%m-%d"
        )
        
        parser = CSVParser()
        
        with pytest.raises(CSVParserError):
            parser.parse_csv(csv_content, template)
    
    def test_parse_csv_with_invalid_amount(self):
        """Test parsing a CSV file with an invalid amount."""
        csv_content = """Date,Amount,Description
2023-01-01,not-a-number,Grocery Store
2023-01-02,-50.25,Gas Station
"""
        
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description"
            },
            date_format="%Y-%m-%d"
        )
        
        parser = CSVParser()
        
        with pytest.raises(CSVParserError):
            parser.parse_csv(csv_content, template)


class TestQIFParser:
    """Tests for the QIFParser class."""
    
    def test_parse_bank_transactions(self):
        """Test parsing bank transactions from QIF content."""
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
        
        parser = QIFParser()
        
        qif_file = parser.parse(qif_content)
        
        assert len(qif_file.bank_transactions) == 1  # One account
        assert "Default" in qif_file.bank_transactions  # Default account name
        assert len(qif_file.bank_transactions["Default"]) == 2  # Two transactions
        
        transaction = qif_file.bank_transactions["Default"][0]
        assert transaction.date == datetime(2023, 1, 15)
        assert transaction.amount == 100.50
        assert transaction.payee == "Grocery Store"
        assert transaction.number == "123"
        assert transaction.memo == "Weekly groceries"
        assert transaction.category == "Food:Groceries"
        
        transaction = qif_file.bank_transactions["Default"][1]
        assert transaction.date == datetime(2023, 2, 28)
        assert transaction.amount == -50.25
        assert transaction.payee == "Gas Station"
        assert transaction.memo == "Fill up car"
        assert transaction.category == "Auto:Fuel"
    
    def test_parse_investment_transactions(self):
        """Test parsing investment transactions from QIF content."""
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
D02/28/2023
NSell
YMSFT
Q5
I250.25
T1251.25
O6.25
PBroker
MSell Microsoft stock
LInvestments:Stocks
^
"""
        
        parser = QIFParser()
        
        qif_file = parser.parse(qif_content)
        
        assert len(qif_file.investment_transactions) == 1  # One account
        assert "Default" in qif_file.investment_transactions  # Default account name
        assert len(qif_file.investment_transactions["Default"]) == 2  # Two transactions
        
        transaction = qif_file.investment_transactions["Default"][0]
        assert transaction.date == datetime(2023, 1, 15)
        assert transaction.action == "Buy"
        assert transaction.security == "AAPL"
        assert transaction.quantity == 10
        assert transaction.price == 150.75
        assert transaction.amount == -1507.50
        assert transaction.commission == 7.50
        assert transaction.payee == "Broker"
        assert transaction.memo == "Buy Apple stock"
        assert transaction.category == "Investments:Stocks"
        
        transaction = qif_file.investment_transactions["Default"][1]
        assert transaction.date == datetime(2023, 2, 28)
        assert transaction.action == "Sell"
        assert transaction.security == "MSFT"
        assert transaction.quantity == 5
        assert transaction.price == 250.25
        assert transaction.amount == 1251.25
        assert transaction.commission == 6.25
    
    def test_parse_multiple_accounts(self):
        """Test parsing QIF content with multiple accounts."""
        qif_content = """!Account
NChecking
TBank
^
!Type:Bank
D01/15/2023
T100.50
PGrocery Store
^
!Account
NSavings
TBank
^
!Type:Bank
D02/28/2023
T-50.25
PGas Station
^
!Account
NInvestments
TInvst
^
!Type:Invst
D03/15/2023
NBuy
YAAPL
Q10
I150.75
T-1507.50
^
"""
        
        parser = QIFParser()
        
        qif_file = parser.parse(qif_content)
        
        assert len(qif_file.accounts) == 3
        assert qif_file.accounts[0].name == "Checking"
        assert qif_file.accounts[0].type == AccountType.BANK
        assert qif_file.accounts[1].name == "Savings"
        assert qif_file.accounts[1].type == AccountType.BANK
        assert qif_file.accounts[2].name == "Investments"
        assert qif_file.accounts[2].type == AccountType.INVESTMENT
        
        assert "Checking" in qif_file.bank_transactions
        assert len(qif_file.bank_transactions["Checking"]) == 1
        assert "Savings" in qif_file.bank_transactions
        assert len(qif_file.bank_transactions["Savings"]) == 1
        assert "Investments" in qif_file.investment_transactions
        assert len(qif_file.investment_transactions["Investments"]) == 1
    
    def test_parse_split_transactions(self):
        """Test parsing QIF content with split transactions."""
        qif_content = """!Type:Bank
D01/15/2023
T150.75
PGrocery Store
MSplit purchase
SFood:Groceries
$100.50
SHousehold:Supplies
$50.25
^
"""
        
        parser = QIFParser()
        
        qif_file = parser.parse(qif_content)
        
        assert "Default" in qif_file.bank_transactions
        assert len(qif_file.bank_transactions["Default"]) == 1
        
        transaction = qif_file.bank_transactions["Default"][0]
        assert transaction.date == datetime(2023, 1, 15)
        assert transaction.amount == 150.75
        assert transaction.payee == "Grocery Store"
        assert transaction.memo == "Split purchase"
        
        assert len(transaction.splits) == 2
        assert transaction.splits[0].category == "Food:Groceries"
        assert transaction.splits[0].amount == 100.50
        assert transaction.splits[1].category == "Household:Supplies"
        assert transaction.splits[1].amount == 50.25
    
    def test_parse_invalid_qif(self):
        """Test parsing invalid QIF content."""
        qif_content = """!Type:Bank
D01/15/2023
T100.50
PGrocery Store
D02/28/2023
T-50.25
PGas Station
"""
        
        parser = QIFParser()
        
        with pytest.raises(QIFParserError):
            parser.parse(qif_content)
    
    def test_parse_qif_with_invalid_date(self):
        """Test parsing QIF content with an invalid date."""
        qif_content = """!Type:Bank
Dinvalid-date
T100.50
PGrocery Store
^
"""
        
        parser = QIFParser()
        
        with pytest.raises(QIFParserError):
            parser.parse(qif_content)
    
    def test_parse_qif_with_invalid_amount(self):
        """Test parsing QIF content with an invalid amount."""
        qif_content = """!Type:Bank
D01/15/2023
Tnot-a-number
PGrocery Store
^
"""
        
        parser = QIFParser()
        
        with pytest.raises(QIFParserError):
            parser.parse(qif_content)
