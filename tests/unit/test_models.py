import pytest
from datetime import datetime
from decimal import Decimal

from quickenqifimport.models.models import (
    BaseTransaction, BankingTransaction, InvestmentTransaction,
    SplitTransaction, AccountDefinition, QIFFile, CSVTemplate,
    AccountType
)

class TestBaseTransaction:
    """Tests for the BaseTransaction model."""
    
    def test_base_transaction_creation(self):
        """Test creating a base transaction."""
        transaction = BaseTransaction(
            date=datetime(2023, 1, 1),
            amount=100.50,
            memo="Test memo",
            cleared_status="*"
        )
        
        assert transaction.date == datetime(2023, 1, 1)
        assert transaction.amount == 100.50
        assert transaction.memo == "Test memo"
        assert transaction.cleared_status == "*"
    
    def test_base_transaction_defaults(self):
        """Test default values for base transaction."""
        transaction = BaseTransaction(
            date=datetime(2023, 1, 1),
            amount=100.50
        )
        
        assert transaction.memo is None
        assert transaction.cleared_status == ""

class TestBankingTransaction:
    """Tests for the BankingTransaction model."""
    
    def test_banking_transaction_creation(self):
        """Test creating a banking transaction."""
        transaction = BankingTransaction(
            date=datetime(2023, 1, 1),
            amount=100.50,
            payee="Test Payee",
            number="123",
            memo="Test memo",
            category="Test:Category",
            cleared_status="*",
            address=["123 Main St", "Anytown, USA"]
        )
        
        assert transaction.date == datetime(2023, 1, 1)
        assert transaction.amount == 100.50
        assert transaction.payee == "Test Payee"
        assert transaction.number == "123"
        assert transaction.memo == "Test memo"
        assert transaction.category == "Test:Category"
        assert transaction.cleared_status == "*"
        assert transaction.address == ["123 Main St", "Anytown, USA"]
        assert transaction.splits is None
    
    def test_banking_transaction_with_splits(self):
        """Test banking transaction with split transactions."""
        split1 = SplitTransaction(
            category="Split1:Category",
            amount=60.00,
            memo="Split 1 memo"
        )
        
        split2 = SplitTransaction(
            category="Split2:Category",
            amount=40.50,
            memo="Split 2 memo"
        )
        
        transaction = BankingTransaction(
            date=datetime(2023, 1, 1),
            amount=100.50,
            payee="Test Payee",
            memo="Test memo",
            splits=[split1, split2]
        )
        
        assert len(transaction.splits) == 2
        assert transaction.splits[0].category == "Split1:Category"
        assert transaction.splits[0].amount == 60.00
        assert transaction.splits[0].memo == "Split 1 memo"
        assert transaction.splits[1].category == "Split2:Category"
        assert transaction.splits[1].amount == 40.50
        assert transaction.splits[1].memo == "Split 2 memo"
        
        assert sum(split.amount for split in transaction.splits) == transaction.amount

class TestInvestmentTransaction:
    """Tests for the InvestmentTransaction model."""
    
    def test_investment_transaction_creation(self):
        """Test creating an investment transaction."""
        transaction = InvestmentTransaction(
            date=datetime(2023, 1, 1),
            action="Buy",
            security="AAPL",
            quantity=10,
            price=150.75,
            amount=-1507.50,
            commission=7.50,
            payee="Broker",
            memo="Buy Apple stock",
            account="Investment Account",
            cleared_status="*"
        )
        
        assert transaction.date == datetime(2023, 1, 1)
        assert transaction.action == "Buy"
        assert transaction.security == "AAPL"
        assert transaction.quantity == 10
        assert transaction.price == 150.75
        assert transaction.amount == -1507.50
        assert transaction.commission == 7.50
        assert transaction.payee == "Broker"
        assert transaction.memo == "Buy Apple stock"
        assert transaction.account == "Investment Account"
        assert transaction.cleared_status == "*"
    
    def test_investment_transaction_defaults(self):
        """Test default values for investment transaction."""
        transaction = InvestmentTransaction(
            date=datetime(2023, 1, 1),
            action="Buy",
            security="AAPL",
            amount=-1507.50
        )
        
        assert transaction.quantity is None
        assert transaction.price is None
        assert transaction.commission is None
        assert transaction.payee is None
        assert transaction.memo is None
        assert transaction.account is None
        assert transaction.cleared_status == ""

class TestSplitTransaction:
    """Tests for the SplitTransaction model."""
    
    def test_split_transaction_creation(self):
        """Test creating a split transaction."""
        split = SplitTransaction(
            category="Test:Category",
            amount=50.25,
            memo="Split memo"
        )
        
        assert split.category == "Test:Category"
        assert split.amount == 50.25
        assert split.memo == "Split memo"
    
    def test_split_transaction_defaults(self):
        """Test default values for split transaction."""
        split = SplitTransaction(
            category="Test:Category",
            amount=50.25
        )
        
        assert split.memo is None

class TestAccountDefinition:
    """Tests for the AccountDefinition model."""
    
    def test_account_definition_creation(self):
        """Test creating an account definition."""
        account = AccountDefinition(
            name="Test Account",
            type=AccountType.BANK,
            description="Test account description"
        )
        
        assert account.name == "Test Account"
        assert account.type == AccountType.BANK
        assert account.description == "Test account description"
    
    def test_account_definition_defaults(self):
        """Test default values for account definition."""
        account = AccountDefinition(
            name="Test Account",
            type=AccountType.BANK
        )
        
        assert account.description is None

class TestQIFFile:
    """Tests for the QIFFile model."""
    
    def test_qif_file_creation(self):
        """Test creating a QIF file."""
        qif_file = QIFFile()
        
        assert qif_file.accounts == []
        assert qif_file.bank_transactions == {}
        assert qif_file.cash_transactions == {}
        assert qif_file.credit_card_transactions == {}
        assert qif_file.investment_transactions == {}
        assert qif_file.asset_transactions == {}
        assert qif_file.liability_transactions == {}
        assert qif_file.categories == []
        assert qif_file.classes == []
        assert qif_file.memorized_transactions == []
    
    def test_qif_file_with_accounts_and_transactions(self):
        """Test QIF file with accounts and transactions."""
        bank_account = AccountDefinition(
            name="Checking Account",
            type=AccountType.BANK,
            description="Primary checking account"
        )
        
        investment_account = AccountDefinition(
            name="Investment Account",
            type=AccountType.INVESTMENT,
            description="Investment account"
        )
        
        bank_transaction = BankingTransaction(
            date=datetime(2023, 1, 1),
            amount=100.50,
            payee="Test Payee",
            memo="Test memo"
        )
        
        investment_transaction = InvestmentTransaction(
            date=datetime(2023, 1, 2),
            action="Buy",
            security="AAPL",
            quantity=10,
            price=150.75,
            amount=-1507.50
        )
        
        qif_file = QIFFile()
        qif_file.accounts = [bank_account, investment_account]
        qif_file.bank_transactions = {"Checking Account": [bank_transaction]}
        qif_file.investment_transactions = {"Investment Account": [investment_transaction]}
        
        assert len(qif_file.accounts) == 2
        assert qif_file.accounts[0].name == "Checking Account"
        assert qif_file.accounts[1].name == "Investment Account"
        
        assert len(qif_file.bank_transactions["Checking Account"]) == 1
        assert qif_file.bank_transactions["Checking Account"][0].amount == 100.50
        
        assert len(qif_file.investment_transactions["Investment Account"]) == 1
        assert qif_file.investment_transactions["Investment Account"][0].security == "AAPL"

class TestCSVTemplate:
    """Tests for the CSVTemplate model."""
    
    def test_csv_template_creation(self):
        """Test creating a CSV template."""
        template = CSVTemplate(
            name="Test Template",
            description="Test template description",
            account_type=AccountType.BANK,
            delimiter=",",
            date_format="%Y-%m-%d",
            has_header=True,
            skip_rows=1,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description",
                "memo": "Notes"
            },
            amount_columns=["Amount"],
            amount_multiplier={"Amount": 1.0},
            category_format="Category:Subcategory",
            detect_transfers=True,
            transfer_pattern=r"\[(.*?)\]"
        )
        
        assert template.name == "Test Template"
        assert template.description == "Test template description"
        assert template.account_type == AccountType.BANK
        assert template.delimiter == ","
        assert template.date_format == "%Y-%m-%d"
        assert template.has_header is True
        assert template.skip_rows == 1
        assert template.field_mapping == {
            "date": "Date",
            "amount": "Amount",
            "payee": "Description",
            "memo": "Notes"
        }
        assert template.amount_columns == ["Amount"]
        assert template.amount_multiplier == {"Amount": 1.0}
        assert template.category_format == "Category:Subcategory"
        assert template.detect_transfers is True
        assert template.transfer_pattern == r"\[(.*?)\]"
    
    def test_csv_template_defaults(self):
        """Test default values for CSV template."""
        template = CSVTemplate(
            name="Test Template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount"
            }
        )
        
        assert template.description is None
        assert template.delimiter == ","
        assert template.date_format == "%Y-%m-%d"
        assert template.has_header is True
        assert template.skip_rows == 0
        assert template.amount_columns == []
        assert template.amount_multiplier is None
        assert template.category_format is None
        assert template.detect_transfers is True
        assert template.transfer_pattern == r"^\[(.+)\]$"
