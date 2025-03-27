import pytest
from datetime import datetime
from pydantic import ValidationError

from quickenqifimport.models.models import (
    AccountType, QIFFile, BankingTransaction, InvestmentTransaction,
    InvestmentAction, ClearedStatus, SplitTransaction, CSVTemplate
)

class TestModelsValidation:
    """Unit tests for model validation."""
    
    def test_banking_transaction_validation(self):
        """Test BankingTransaction validation."""
        transaction = BankingTransaction(
            date=datetime(2023, 1, 15),
            amount=-50.25,
            payee="Gas Station",
            memo="Fill up car",
            category="Auto:Fuel"
        )
        assert transaction.date == datetime(2023, 1, 15)
        assert transaction.amount == -50.25
        assert transaction.payee == "Gas Station"
        assert transaction.memo == "Fill up car"
        assert transaction.category == "Auto:Fuel"
        
        with pytest.raises(ValidationError):
            BankingTransaction(
                date="invalid-date",
                amount=-50.25,
                payee="Gas Station"
            )
        
        with pytest.raises(ValidationError):
            BankingTransaction(
                date=datetime(2023, 1, 15),
                amount="invalid-amount",
                payee="Gas Station"
            )
    
    def test_investment_transaction_validation(self):
        """Test InvestmentTransaction validation."""
        transaction = InvestmentTransaction(
            date=datetime(2023, 1, 15),
            action=InvestmentAction.BUY,
            security="AAPL",
            quantity=10,
            price=150.75,
            amount=-1507.50,
            commission=7.50,
            memo="Buy Apple stock"
        )
        assert transaction.date == datetime(2023, 1, 15)
        assert transaction.action == InvestmentAction.BUY
        assert transaction.security == "AAPL"
        assert transaction.quantity == 10
        assert transaction.price == 150.75
        assert transaction.amount == -1507.50
        assert transaction.commission == 7.50
        assert transaction.memo == "Buy Apple stock"
        
        with pytest.raises(ValidationError):
            InvestmentTransaction(
                date=datetime(2023, 1, 15),
                action="invalid-action",
                security="AAPL",
                quantity=10,
                price=150.75,
                amount=-1507.50
            )
        
        with pytest.raises(ValidationError):
            InvestmentTransaction(
                date=datetime(2023, 1, 15),
                action=InvestmentAction.BUY,
                security="AAPL",
                quantity="invalid-quantity",
                price=150.75,
                amount=-1507.50
            )
    
    def test_split_transaction_validation(self):
        """Test SplitTransaction validation."""
        split = SplitTransaction(
            category="Food:Groceries",
            amount=-100.50,
            memo="Groceries"
        )
        assert split.category == "Food:Groceries"
        assert split.amount == -100.50
        assert split.memo == "Groceries"
        
        with pytest.raises(ValidationError):
            SplitTransaction(
                category="Food:Groceries",
                amount="invalid-amount",
                memo="Groceries"
            )
    
    def test_qif_file_validation(self):
        """Test QIFFile validation."""
        bank_transactions = {
            "Checking": [
                BankingTransaction(
                    date=datetime(2023, 1, 15),
                    amount=-50.25,
                    payee="Gas Station",
                    memo="Fill up car",
                    category="Auto:Fuel"
                ),
                BankingTransaction(
                    date=datetime(2023, 1, 16),
                    amount=1200.00,
                    payee="Paycheck",
                    memo="January salary",
                    category="Income:Salary"
                )
            ]
        }
        
        qif_file = QIFFile(bank_transactions=bank_transactions)
        assert len(qif_file.bank_transactions) == 1
        assert len(qif_file.bank_transactions["Checking"]) == 2
        
        investment_transactions = {
            "Brokerage": [
                InvestmentTransaction(
                    date=datetime(2023, 1, 15),
                    action=InvestmentAction.BUY,
                    security="AAPL",
                    quantity=10,
                    price=150.75,
                    amount=-1507.50
                )
            ]
        }
        
        qif_file = QIFFile(investment_transactions=investment_transactions)
        assert len(qif_file.investment_transactions) == 1
        assert len(qif_file.investment_transactions["Brokerage"]) == 1
    
    def test_csv_template_validation(self):
        """Test CSVTemplate validation."""
        template = CSVTemplate(
            name="bank_template",
            account_type=AccountType.BANK,
            field_mapping={
                "date": "Date",
                "amount": "Amount",
                "payee": "Description"
            },
            date_format="%Y-%m-%d"
        )
        assert template.name == "bank_template"
        assert template.account_type == AccountType.BANK
        assert template.field_mapping["date"] == "Date"
        assert template.field_mapping["amount"] == "Amount"
        assert template.field_mapping["payee"] == "Description"
        assert template.date_format == "%Y-%m-%d"
        
        with pytest.raises(ValidationError):
            CSVTemplate(
                name="bank_template",
                account_type=AccountType.BANK
            )
        
        with pytest.raises(ValidationError):
            CSVTemplate(
                name="bank_template",
                account_type=AccountType.BANK,
                field_mapping="invalid-field-mapping"
            )
    
    def test_date_parsing(self):
        """Test date parsing in transactions."""
        transaction = BankingTransaction(
            date="2023-01-15",
            amount=-50.25,
            payee="Gas Station"
        )
        assert transaction.date == datetime(2023, 1, 15)
        
        transaction = BankingTransaction(
            date="01/15/2023",
            amount=-50.25,
            payee="Gas Station"
        )
        assert transaction.date == datetime(2023, 1, 15)
        
        transaction = BankingTransaction(
            date="15-01-2023",
            amount=-50.25,
            payee="Gas Station"
        )
        assert transaction.date == datetime(2023, 1, 15)
    
    def test_cleared_status(self):
        """Test cleared status in transactions."""
        transaction = BankingTransaction(
            date=datetime(2023, 1, 15),
            amount=-50.25,
            payee="Gas Station"
        )
        assert transaction.cleared_status == ClearedStatus.UNCLEARED
        
        transaction = BankingTransaction(
            date=datetime(2023, 1, 15),
            amount=-50.25,
            payee="Gas Station",
            cleared_status=ClearedStatus.CLEARED
        )
        assert transaction.cleared_status == ClearedStatus.CLEARED
        
        transaction = BankingTransaction(
            date=datetime(2023, 1, 15),
            amount=-50.25,
            payee="Gas Station",
            cleared_status=ClearedStatus.RECONCILED
        )
        assert transaction.cleared_status == ClearedStatus.RECONCILED
