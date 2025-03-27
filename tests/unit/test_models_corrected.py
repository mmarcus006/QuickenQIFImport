import pytest
from datetime import datetime
from decimal import Decimal

from quickenqifimport.models.models import (
    AccountType, TransactionType, InvestmentAction, 
    Transaction, InvestmentTransaction, CSVTemplate
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
    
    def test_transaction_type_enum(self):
        """Test TransactionType enum values."""
        assert TransactionType.BANK.value == "Bank"
        assert TransactionType.CASH.value == "Cash"
        assert TransactionType.CREDIT_CARD.value == "CCard"
        assert TransactionType.INVESTMENT.value == "Invst"
        assert TransactionType.ASSET.value == "Oth A"
        assert TransactionType.LIABILITY.value == "Oth L"
        assert TransactionType.MEMORIZED.value == "Memorized"
    
    def test_investment_action_enum(self):
        """Test InvestmentAction enum values."""
        assert InvestmentAction.BUY.value == "Buy"
        assert InvestmentAction.SELL.value == "Sell"
        assert InvestmentAction.DIVIDEND.value == "Div"
        assert InvestmentAction.INTEREST.value == "IntInc"
        assert InvestmentAction.TRANSFER.value == "XIn"
        assert InvestmentAction.REMOVE.value == "XOut"
        assert InvestmentAction.REINVEST.value == "ReinvDiv"
        assert InvestmentAction.ADD_SHARES.value == "ShrsIn"
        assert InvestmentAction.REMOVE_SHARES.value == "ShrsOut"
        assert InvestmentAction.STOCK_SPLIT.value == "StkSplit"
    
    def test_transaction_model(self):
        """Test Transaction model creation and validation."""
        transaction = Transaction(
            date=datetime(2023, 1, 15),
            amount=Decimal("100.50"),
            payee="Test Payee",
            category="Income:Salary",
            memo="Test memo",
            number="123",
            cleared_status="*",
            address="123 Main St\nAnytown, US 12345"
        )
        
        assert transaction.date == datetime(2023, 1, 15)
        assert transaction.amount == Decimal("100.50")
        assert transaction.payee == "Test Payee"
        assert transaction.category == "Income:Salary"
        assert transaction.memo == "Test memo"
        assert transaction.number == "123"
        assert transaction.cleared_status == "*"
        assert transaction.address == "123 Main St\nAnytown, US 12345"
    
    def test_transaction_model_defaults(self):
        """Test Transaction model default values."""
        transaction = Transaction(
            date=datetime(2023, 1, 15),
            amount=Decimal("100.50")
        )
        
        assert transaction.date == datetime(2023, 1, 15)
        assert transaction.amount == Decimal("100.50")
        assert transaction.payee is None
        assert transaction.category is None
        assert transaction.memo is None
        assert transaction.number is None
        assert transaction.cleared_status is None
        assert transaction.address is None
    
    def test_investment_transaction_model(self):
        """Test InvestmentTransaction model creation and validation."""
        transaction = InvestmentTransaction(
            date=datetime(2023, 1, 15),
            action=InvestmentAction.BUY,
            security="AAPL",
            quantity=Decimal("10"),
            price=Decimal("150.75"),
            amount=Decimal("1507.50"),
            commission=Decimal("9.99"),
            memo="Buy Apple stock",
            category="Investments:Stocks",
            account="Brokerage Account"
        )
        
        assert transaction.date == datetime(2023, 1, 15)
        assert transaction.action == InvestmentAction.BUY
        assert transaction.security == "AAPL"
        assert transaction.quantity == Decimal("10")
        assert transaction.price == Decimal("150.75")
        assert transaction.amount == Decimal("1507.50")
        assert transaction.commission == Decimal("9.99")
        assert transaction.memo == "Buy Apple stock"
        assert transaction.category == "Investments:Stocks"
        assert transaction.account == "Brokerage Account"
    
    def test_investment_transaction_model_defaults(self):
        """Test InvestmentTransaction model default values."""
        transaction = InvestmentTransaction(
            date=datetime(2023, 1, 15),
            action=InvestmentAction.BUY,
            security="AAPL",
            quantity=Decimal("10"),
            price=Decimal("150.75"),
            amount=Decimal("1507.50")
        )
        
        assert transaction.date == datetime(2023, 1, 15)
        assert transaction.action == InvestmentAction.BUY
        assert transaction.security == "AAPL"
        assert transaction.quantity == Decimal("10")
        assert transaction.price == Decimal("150.75")
        assert transaction.amount == Decimal("1507.50")
        assert transaction.commission == Decimal("0")
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
        assert template.date_format == "%m/%d/%Y"
        assert template.skip_rows == 0
        assert template.amount_columns == ["Amount"]
        assert template.amount_multiplier == {}
        assert template.category_format == ":"
        assert template.detect_transfers is False
        assert template.transfer_pattern == r"\[(.*?)\]"
