import pytest
from datetime import datetime
import os
import tempfile

from quickenqifimport.services.csv_to_qif_service import CSVToQIFService, CSVToQIFServiceError
from quickenqifimport.services.qif_to_csv_service import QIFToCSVService, QIFToCSVServiceError
from quickenqifimport.services.transfer_recognition_service import TransferRecognitionService
from quickenqifimport.models.models import (
    CSVTemplate, AccountType, BankingTransaction, InvestmentTransaction,
    SplitTransaction, QIFFile, AccountDefinition
)

class TestCSVToQIFService:
    """Tests for the CSVToQIFService class."""
    
    def test_convert_csv_to_qif(self):
        """Test converting CSV content to QIF content."""
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
        
        service = CSVToQIFService()
        
        qif_content = service.convert_csv_to_qif(csv_content, template)
        
        assert "!Type:Bank" in qif_content
        assert "D01/01/2023" in qif_content
        assert "T100.50" in qif_content
        assert "PGrocery Store" in qif_content
        assert "N123" in qif_content
        assert "MWeekly groceries" in qif_content
        assert "LFood:Groceries" in qif_content
        assert "D01/02/2023" in qif_content
        assert "T-50.25" in qif_content
        assert "PGas Station" in qif_content
        assert "MFill up car" in qif_content
        assert "LAuto:Fuel" in qif_content
        assert "D01/03/2023" in qif_content
        assert "T1200.00" in qif_content
        assert "PPaycheck" in qif_content
        assert "NDIRECT DEP" in qif_content
        assert "MJanuary salary" in qif_content
        assert "LIncome:Salary" in qif_content
        
        assert qif_content.count("^") == 4  # Account section + 3 transactions
    
    def test_convert_csv_to_qif_with_account_name(self):
        """Test converting CSV content to QIF content with an account name."""
        csv_content = """Date,Amount,Description
2023-01-01,100.50,Grocery Store
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
        
        service = CSVToQIFService()
        
        qif_content = service.convert_csv_to_qif(csv_content, template, account_name="Checking")
        
        assert "!Account" in qif_content
        assert "NChecking" in qif_content
        assert "TBank" in qif_content
        assert "!Type:Bank" in qif_content
    
    def test_convert_investment_csv_to_qif(self):
        """Test converting investment CSV content to QIF content."""
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
        
        service = CSVToQIFService()
        
        qif_content = service.convert_csv_to_qif(csv_content, template)
        
        assert "!Type:Invst" in qif_content
        assert "D01/01/2023" in qif_content
        assert "N" in qif_content  # Just check for action indicator
        assert "YAAPL" in qif_content
        assert "Q10" in qif_content
        assert "I150.75" in qif_content
        assert "T-1507.50" in qif_content
        assert "O7.50" in qif_content
        assert "PBroker" in qif_content
        assert "MBuy Apple stock" in qif_content
        assert "LInvestments:Stocks" in qif_content
        assert "D01/02/2023" in qif_content
        assert "YMSFT" in qif_content
        assert "Q5" in qif_content
        assert "I250.25" in qif_content
        assert "T1251.25" in qif_content
        assert "O6.25" in qif_content
        assert "D01/03/2023" in qif_content
        assert "YVTI" in qif_content
        assert "PVanguard" in qif_content
        assert "MDividend payment" in qif_content
        assert "LIncome:Dividends" in qif_content
        
        assert qif_content.count("^") == 4  # Account section + 3 transactions
    
    def test_convert_csv_to_qif_with_invalid_csv(self):
        """Test converting invalid CSV content to QIF content."""
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
        
        service = CSVToQIFService()
        
        with pytest.raises(CSVToQIFServiceError):
            service.convert_csv_to_qif(csv_content, template)
    
    def test_convert_csv_file_to_qif_file(self, tmp_path):
        """Test converting a CSV file to a QIF file."""
        csv_file = tmp_path / "test.csv"
        csv_content = """Date,Amount,Description
2023-01-01,100.50,Grocery Store
2023-01-02,-50.25,Gas Station
"""
        csv_file.write_text(csv_content)
        
        qif_file = tmp_path / "test.qif"
        
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
        
        service = CSVToQIFService()
        
        service.convert_csv_file_to_qif_file(str(csv_file), template, str(qif_file))
        
        assert qif_file.exists()
        
        qif_content = qif_file.read_text()
        assert "!Type:Bank" in qif_content
        assert "D01/01/2023" in qif_content
        assert "T100.50" in qif_content
        assert "PGrocery Store" in qif_content
        assert "D01/02/2023" in qif_content
        assert "T-50.25" in qif_content
        assert "PGas Station" in qif_content


class TestQIFToCSVService:
    """Tests for the QIFToCSVService class."""
    
    def test_convert_qif_to_csv(self):
        """Test converting QIF content to CSV content."""
        qif_content = """!Type:Bank
D01/01/2023
T100.50
PGrocery Store
N123
MWeekly groceries
LFood:Groceries
^
D01/02/2023
T-50.25
PGas Station
MFill up car
LAuto:Fuel
^
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
        
        service = QIFToCSVService()
        
        csv_content = service.convert_qif_to_csv(qif_content, template)
        
        assert "Date,Amount,Description,Reference,Notes,Category" in csv_content
        assert "2023-01-01,100.5,Grocery Store,123,Weekly groceries,Food:Groceries" in csv_content
        assert "2023-01-02,-50.25,Gas Station,,Fill up car,Auto:Fuel" in csv_content
    
    def test_convert_investment_qif_to_csv(self):
        """Test converting investment QIF content to CSV content."""
        qif_content = """!Type:Invst
D01/01/2023
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
D01/02/2023
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
        
        service = QIFToCSVService()
        
        csv_content = service.convert_qif_to_csv(qif_content, template)
        
        assert "Date,Action,Security,Quantity,Price,Amount,Commission,Description,Memo,Category" in csv_content
        assert "2023-01-01,Buy,AAPL,10,150.75,-1507.5,7.5,Broker,Buy Apple stock,Investments:Stocks" in csv_content
        assert "2023-01-02,Sell,MSFT,5,250.25,1251.25,6.25,Broker,Sell Microsoft stock,Investments:Stocks" in csv_content
    
    def test_convert_qif_to_csv_with_account_name(self):
        """Test converting QIF content to CSV content with an account name."""
        qif_content = """!Account
NChecking
TBank
^
!Type:Bank
D01/01/2023
T100.50
PGrocery Store
^
D01/02/2023
T-50.25
PGas Station
^
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
        
        service = QIFToCSVService()
        
        csv_content = service.convert_qif_to_csv(qif_content, template, account_name="Checking")
        
        assert "Date,Amount,Description" in csv_content
        assert "2023-01-01,100.5,Grocery Store" in csv_content
        assert "2023-01-02,-50.25,Gas Station" in csv_content
    
    def test_convert_qif_to_csv_with_invalid_qif(self):
        """Test converting invalid QIF content to CSV content."""
        qif_content = """!Type:Bank
D01/01/2023
Tnot-a-number
PGrocery Store
^
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
        
        service = QIFToCSVService()
        
        with pytest.raises(QIFToCSVServiceError):
            service.convert_qif_to_csv(qif_content, template)
    
    def test_convert_qif_file_to_csv_file(self, tmp_path):
        """Test converting a QIF file to a CSV file."""
        qif_file = tmp_path / "test.qif"
        qif_content = """!Type:Bank
D01/01/2023
T100.50
PGrocery Store
^
D01/02/2023
T-50.25
PGas Station
^
"""
        qif_file.write_text(qif_content)
        
        csv_file = tmp_path / "test.csv"
        
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
        
        service = QIFToCSVService()
        
        service.convert_qif_file_to_csv_file(str(qif_file), template, str(csv_file))
        
        assert csv_file.exists()
        
        csv_content = csv_file.read_text()
        assert "Date,Amount,Description" in csv_content
        assert "2023-01-01,100.5,Grocery Store" in csv_content
        assert "2023-01-02,-50.25,Gas Station" in csv_content


class TestTransferRecognitionService:
    """Tests for the TransferRecognitionService class."""
    
    def test_process_transfers(self):
        """Test processing transfers between accounts."""
        transactions = [
            BankingTransaction(
                date=datetime(2023, 1, 1),
                amount=100.50,
                payee="Transfer to Savings",
                account="Checking"
            ),
            BankingTransaction(
                date=datetime(2023, 1, 1),
                amount=-100.50,
                payee="Transfer from Checking",
                account="Savings"
            ),
            BankingTransaction(
                date=datetime(2023, 1, 2),
                amount=50.25,
                payee="Gas Station",
                account="Checking"
            )
        ]
        
        service = TransferRecognitionService()
        
        processed_transactions = service.process_transfers(transactions)
        
        assert len(processed_transactions) == 3
        
        assert processed_transactions[0].category == "[Savings]"
        assert processed_transactions[1].category == "[Checking]"
        assert processed_transactions[2].category is None
    
    def test_process_transfers_with_date_difference(self):
        """Test processing transfers with a date difference."""
        transactions = [
            BankingTransaction(
                date=datetime(2023, 1, 1),
                amount=100.50,
                payee="Transfer to Savings",
                account="Checking"
            ),
            BankingTransaction(
                date=datetime(2023, 1, 2),  # One day later
                amount=-100.50,
                payee="Transfer from Checking",
                account="Savings"
            )
        ]
        
        service = TransferRecognitionService(max_date_difference=1)
        
        processed_transactions = service.process_transfers(transactions)
        
        assert processed_transactions[0].category == "[Savings]"
        assert processed_transactions[1].category == "[Checking]"
    
    def test_process_transfers_with_amount_tolerance(self):
        """Test processing transfers with an amount tolerance."""
        transactions = [
            BankingTransaction(
                date=datetime(2023, 1, 1),
                amount=100.50,
                payee="Transfer to Savings",
                account="Checking"
            ),
            BankingTransaction(
                date=datetime(2023, 1, 1),
                amount=-100.45,  # Slightly different amount
                payee="Transfer from Checking",
                account="Savings"
            )
        ]
        
        service = TransferRecognitionService(amount_tolerance=0.1)
        
        processed_transactions = service.process_transfers(transactions)
        
        assert processed_transactions[0].category == "[Savings]"
        assert processed_transactions[1].category == "[Checking]"
    
    def test_process_transfers_with_investment_transactions(self):
        """Test processing transfers with investment transactions."""
        transactions = [
            InvestmentTransaction(
                date=datetime(2023, 1, 1),
                action="Buy",
                security="AAPL",
                quantity=10,
                price=150.75,
                amount=-1507.50,
                account="Investment Account"
            ),
            InvestmentTransaction(
                date=datetime(2023, 1, 1),
                action="Sell",
                security="MSFT",
                quantity=5,
                price=250.25,
                amount=1251.25,
                account="Investment Account"
            )
        ]
        
        service = TransferRecognitionService()
        
        processed_transactions = service.process_transfers(transactions)
        
        assert len(processed_transactions) == 2
        
        assert processed_transactions[0].account == "Investment Account"
        assert processed_transactions[1].account == "Investment Account"
