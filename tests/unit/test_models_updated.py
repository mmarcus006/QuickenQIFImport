import pytest
from datetime import datetime
from decimal import Decimal

from quickenqifimport.models.models import (
    AccountType, InvestmentAction, ClearedStatus, MemorizedTransactionType,
    BaseTransaction, BankingTransaction, InvestmentTransaction, CSVTemplate
)

class TestModels:
    """Unit tests for model classes."""
    
    def test_account_type_enum(self):
        """Test AccountType enum values."""
        assert AccountType.BANK.value == "Bank"
        assert AccountType.CASH.value == "Cash"
        assert AccountType.CREDIT_CARD.value == "CCard"
        assert AccountType.INVESTMENT.value == "Invst"
        assert AccountType.ASSET.value == "Oth A"
        assert AccountType.LIABILITY.value == "Oth L"
        assert AccountType.INVOICE.value == "Invoice"
    
    def test_investment_action_enum(self):
        """Test InvestmentAction enum values."""
        assert InvestmentAction.BUY.value == "Buy"
        assert InvestmentAction.SELL.value == "Sell"
        assert InvestmentAction.DIV.value == "Div"
        assert InvestmentAction.INT_INC.value == "IntInc"
        assert InvestmentAction.SHARES_IN.value == "ShrsIn"
        assert InvestmentAction.SHARES_OUT.value == "ShrsOut"
        assert InvestmentAction.XIN.value == "XIn"
        assert InvestmentAction.XOUT.value == "XOut"
        assert InvestmentAction.STOCK_SPLIT.value == "StkSplit"
    
    def test_cleared_status_enum(self):
        """Test ClearedStatus enum values."""
        assert ClearedStatus.UNCLEARED.value == ""
        assert ClearedStatus.CLEARED.value == "*"
        assert ClearedStatus.CLEARED_ALT.value == "c"
        assert ClearedStatus.RECONCILED.value == "X"
        assert ClearedStatus.RECONCILED_ALT.value == "R"
    
    def test_memorized_transaction_type_enum(self):
        """Test MemorizedTransactionType enum values."""
        assert MemorizedTransactionType.CHECK.value == "KC"
        assert MemorizedTransactionType.DEPOSIT.value == "KD"
        assert MemorizedTransactionType.PAYMENT.value == "KP"
        assert MemorizedTransactionType.INVESTMENT.value == "KI"
        assert MemorizedTransactionType.ELECTRONIC.value == "KE"
    
    def test_base_transaction_model(self):
        """Test BaseTransaction model creation and validation."""
        transaction = BaseTransaction(
            date=datetime(2023, 1, 15),
            amount=100.50,
            memo="Test memo",
            cleared_status=ClearedStatus.CLEARED
        )
        
        assert transaction.date == datetime(2023, 1, 15)
        assert transaction.amount == 100.50
        assert transaction.memo == "Test memo"
        assert transaction.cleared_status == ClearedStatus.CLEARED
    
    def test_base_transaction_model_defaults(self):
        """Test BaseTransaction model default values."""
        transaction = BaseTransaction()
        
        assert transaction.date is None
        assert transaction.amount is None
        assert transaction.memo is None
        assert transaction.cleared_status == ClearedStatus.UNCLEARED
    
    def test_banking_transaction_model(self):
        """Test BankingTransaction model creation and validation."""
        transaction = BankingTransaction(
            date=datetime(2023, 1, 15),
            amount=100.50,
            payee="Test Payee",
            category="Income:Salary",
            memo="Test memo",
            number="123",
            cleared_status=ClearedStatus.CLEARED,
            address=["123 Main St", "Anytown, US 12345"],
            account="Checking Account"
        )
        
        assert transaction.date == datetime(2023, 1, 15)
        assert transaction.amount == 100.50
        assert transaction.payee == "Test Payee"
        assert transaction.category == "Income:Salary"
        assert transaction.memo == "Test memo"
        assert transaction.number == "123"
        assert transaction.cleared_status == ClearedStatus.CLEARED
        assert transaction.address == ["123 Main St", "Anytown, US 12345"]
        assert transaction.account == "Checking Account"
    
    def test_banking_transaction_model_defaults(self):
        """Test BankingTransaction model default values."""
        transaction = BankingTransaction(
            date=datetime(2023, 1, 15),
            amount=100.50
        )
        
        assert transaction.date == datetime(2023, 1, 15)
        assert transaction.amount == 100.50
        assert transaction.payee is None
        assert transaction.category is None
        assert transaction.memo is None
        assert transaction.number is None
        assert transaction.cleared_status == ClearedStatus.UNCLEARED
        assert transaction.address is None
        assert transaction.account is None
    
    def test_banking_transaction_transfer_methods(self):
        """Test BankingTransaction transfer-related methods."""
        transaction = BankingTransaction(
            date=datetime(2023, 1, 15),
            amount=100.50,
            payee="Transfer to Savings",
            category="[Savings Account]",
            memo="Monthly transfer"
        )
        
        assert transaction.is_transfer() is True
        assert transaction.get_transfer_account() == "Savings Account"
        
        transaction = BankingTransaction(
            date=datetime(2023, 1, 15),
            amount=100.50,
            payee="Grocery Store",
            category="Food:Groceries",
            memo="Weekly shopping"
        )
        
        assert transaction.is_transfer() is False
        assert transaction.get_transfer_account() is None
    
    def test_investment_transaction_model(self):
        """Test InvestmentTransaction model creation and validation."""
        transaction = InvestmentTransaction(
            date=datetime(2023, 1, 15),
            action=InvestmentAction.BUY,
            security="AAPL",
            quantity=10.0,
            price=150.75,
            amount=1507.50,
            commission=9.99,
            memo="Buy Apple stock",
            category="Investments:Stocks",
            account="Brokerage Account"
        )
        
        assert transaction.date == datetime(2023, 1, 15)
        assert transaction.action == InvestmentAction.BUY
        assert transaction.security == "AAPL"
        assert transaction.quantity == 10.0
        assert transaction.price == 150.75
        assert transaction.amount == 1507.50
        assert transaction.commission == 9.99
        assert transaction.memo == "Buy Apple stock"
        assert transaction.category == "Investments:Stocks"
        assert transaction.account == "Brokerage Account"
    
    def test_investment_transaction_model_defaults(self):
        """Test InvestmentTransaction model default values."""
        transaction = InvestmentTransaction(
            action=InvestmentAction.BUY
        )
        
        assert transaction.date is None
        assert transaction.action == InvestmentAction.BUY
        assert transaction.security is None
        assert transaction.quantity is None
        assert transaction.price is None
        assert transaction.amount is None
        assert transaction.commission is None
        assert transaction.memo is None
        assert transaction.category is None
        assert transaction.account is None
    
    def test_csv_template_model(self):
        """Test CSVTemplate model creation and validation."""
        template = CSVTemplate(
            name="test_template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description",
                "category": "Category",
                "memo": "Notes"
            },
            delimiter=",",
            has_header=True,
            date_format="%Y-%m-%d",
            skip_rows=1,
            amount_columns=["Amount"],
            amount_multiplier={"Amount": -1},
            category_format="Category:Subcategory",
            detect_transfers=True,
            transfer_pattern=r"\[(.*?)\]"
        )
        
        assert template.name == "test_template"
        assert template.account_type == AccountType.BANK
        assert template.field_mapping["date"] == "Date"
        assert template.field_mapping["amount"] == "Amount"
        assert template.delimiter == ","
        assert template.has_header is True
        assert template.date_format == "%Y-%m-%d"
        assert template.skip_rows == 1
        assert template.amount_columns == ["Amount"]
        assert template.amount_multiplier == {"Amount": -1}
        assert template.category_format == "Category:Subcategory"
        assert template.detect_transfers is True
        assert template.transfer_pattern == r"\[(.*?)\]"
    
    def test_csv_template_model_defaults(self):
        """Test CSVTemplate model default values."""
        template = CSVTemplate(
            name="minimal_template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount"
            }
        )
        
        assert template.name == "minimal_template"
        assert template.account_type == AccountType.BANK
        assert template.field_mapping["date"] == "Date"
        assert template.field_mapping["amount"] == "Amount"
        assert template.delimiter == ","
        assert template.has_header is True
        assert template.date_format == "%Y-%m-%d"  # Default in our implementation
        assert template.skip_rows == 0
        assert template.amount_columns == []  # Empty list by default
        assert template.detect_transfers is True  # Default in our implementation
