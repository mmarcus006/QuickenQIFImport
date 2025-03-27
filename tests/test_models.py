import unittest
from datetime import datetime
from decimal import Decimal

from src.quickenqifimport.models.qif_models import (
    QIFAccountType, QIFClearedStatus, InvestmentAction,
    SplitTransaction, BaseTransaction, BankTransaction,
    CashTransaction, CreditCardTransaction, AssetTransaction,
    LiabilityTransaction, InvestmentTransaction, Account,
    Category, Class, MemorizedTransaction, QIFFile
)
from src.quickenqifimport.models.csv_models import (
    CSVBankTransaction, CSVInvestmentTransaction, CSVTemplate
)


class TestQIFModels(unittest.TestCase):
    """Test cases for QIF models."""
    
    def test_qif_account_type_enum(self):
        """Test QIFAccountType enum."""
        self.assertEqual(QIFAccountType.BANK.value, "Bank")
        self.assertEqual(QIFAccountType.CASH.value, "Cash")
        self.assertEqual(QIFAccountType.CCARD.value, "CCard")
        self.assertEqual(QIFAccountType.INVESTMENT.value, "Invst")
        self.assertEqual(QIFAccountType.ASSET.value, "Oth A")
        self.assertEqual(QIFAccountType.LIABILITY.value, "Oth L")
        self.assertEqual(QIFAccountType.ACCOUNT.value, "Account")
        self.assertEqual(QIFAccountType.CATEGORY.value, "Cat")
        self.assertEqual(QIFAccountType.CLASS.value, "Class")
        self.assertEqual(QIFAccountType.MEMORIZED.value, "Memorized")
    
    def test_qif_cleared_status_enum(self):
        """Test QIFClearedStatus enum."""
        self.assertEqual(QIFClearedStatus.UNCLEARED.value, "")
        self.assertEqual(QIFClearedStatus.CLEARED.value, "*")
        self.assertEqual(QIFClearedStatus.CLEARED_ALT.value, "c")
        self.assertEqual(QIFClearedStatus.RECONCILED.value, "X")
        self.assertEqual(QIFClearedStatus.RECONCILED_ALT.value, "R")
    
    def test_investment_action_enum(self):
        """Test InvestmentAction enum."""
        self.assertEqual(InvestmentAction.BUY.value, "Buy")
        self.assertEqual(InvestmentAction.SELL.value, "Sell")
        self.assertEqual(InvestmentAction.DIVIDEND.value, "Div")
        self.assertEqual(InvestmentAction.REINVEST_DIV.value, "ReinvDiv")
        self.assertEqual(InvestmentAction.SHARES_IN.value, "ShrsIn")
        self.assertEqual(InvestmentAction.SHARES_OUT.value, "ShrsOut")
    
    def test_split_transaction(self):
        """Test SplitTransaction model."""
        split = SplitTransaction(
            category="Groceries",
            memo="Weekly shopping",
            amount=50.0,
            percent=None
        )
        
        self.assertEqual(split.category, "Groceries")
        self.assertEqual(split.memo, "Weekly shopping")
        self.assertEqual(split.amount, 50.0)
        self.assertIsNone(split.percent)
        
        split = SplitTransaction(
            category="Groceries",
            memo="Weekly shopping",
            amount=50.0,
            percent=25.0
        )
        
        self.assertEqual(split.percent, 25.0)
    
    def test_base_transaction(self):
        """Test BaseTransaction model."""
        transaction = BaseTransaction(
            date=datetime(2023, 1, 15),
            amount=100.0,
            cleared_status=QIFClearedStatus.CLEARED,
            number="1234",
            payee="Grocery Store",
            memo="Weekly shopping",
            address=["123 Main St", "Anytown, USA"],
            category="Groceries",
            splits=None,
            reimbursable=True
        )
        
        self.assertEqual(transaction.date, datetime(2023, 1, 15))
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.cleared_status, QIFClearedStatus.CLEARED)
        self.assertEqual(transaction.number, "1234")
        self.assertEqual(transaction.payee, "Grocery Store")
        self.assertEqual(transaction.memo, "Weekly shopping")
        self.assertEqual(transaction.address, ["123 Main St", "Anytown, USA"])
        self.assertEqual(transaction.category, "Groceries")
        self.assertIsNone(transaction.splits)
        self.assertTrue(transaction.reimbursable)
        
        splits = [
            SplitTransaction(category="Food", amount=75.0, memo="Food items"),
            SplitTransaction(category="Household", amount=25.0, memo="Cleaning supplies")
        ]
        
        transaction = BaseTransaction(
            date=datetime(2023, 1, 15),
            amount=100.0,
            cleared_status=QIFClearedStatus.CLEARED,
            number="1234",
            payee="Grocery Store",
            memo="Weekly shopping",
            category=None,
            splits=splits
        )
        
        self.assertEqual(len(transaction.splits), 2)
        self.assertEqual(transaction.splits[0].category, "Food")
        self.assertEqual(transaction.splits[0].amount, 75.0)
        self.assertEqual(transaction.splits[1].category, "Household")
        self.assertEqual(transaction.splits[1].amount, 25.0)
    
    def test_bank_transaction(self):
        """Test BankTransaction model."""
        transaction = BankTransaction(
            date=datetime(2023, 1, 15),
            amount=100.0,
            cleared_status=QIFClearedStatus.CLEARED,
            number="1234",
            payee="Grocery Store",
            memo="Weekly shopping",
            category="Groceries"
        )
        
        self.assertEqual(transaction.date, datetime(2023, 1, 15))
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.cleared_status, QIFClearedStatus.CLEARED)
        self.assertEqual(transaction.number, "1234")
        self.assertEqual(transaction.payee, "Grocery Store")
        self.assertEqual(transaction.memo, "Weekly shopping")
        self.assertEqual(transaction.category, "Groceries")
    
    def test_investment_transaction(self):
        """Test InvestmentTransaction model."""
        transaction = InvestmentTransaction(
            date=datetime(2023, 1, 15),
            action=InvestmentAction.BUY,
            security="AAPL",
            price=150.0,
            quantity=10.0,
            amount=1500.0,
            cleared_status=QIFClearedStatus.CLEARED,
            text="Buy Apple Inc",
            memo="Investment purchase",
            commission=7.99,
            account=None,
            transfer_amount=None
        )
        
        self.assertEqual(transaction.date, datetime(2023, 1, 15))
        self.assertEqual(transaction.action, InvestmentAction.BUY)
        self.assertEqual(transaction.security, "AAPL")
        self.assertEqual(transaction.price, 150.0)
        self.assertEqual(transaction.quantity, 10.0)
        self.assertEqual(transaction.amount, 1500.0)
        self.assertEqual(transaction.cleared_status, QIFClearedStatus.CLEARED)
        self.assertEqual(transaction.text, "Buy Apple Inc")
        self.assertEqual(transaction.memo, "Investment purchase")
        self.assertEqual(transaction.commission, 7.99)
        self.assertIsNone(transaction.account)
        self.assertIsNone(transaction.transfer_amount)
    
    def test_account(self):
        """Test Account model."""
        account = Account(
            name="Checking",
            type=QIFAccountType.BANK,
            description="Primary checking account",
            credit_limit=None,
            statement_date=datetime(2023, 1, 31),
            statement_balance=1250.75
        )
        
        self.assertEqual(account.name, "Checking")
        self.assertEqual(account.type, QIFAccountType.BANK)
        self.assertEqual(account.description, "Primary checking account")
        self.assertIsNone(account.credit_limit)
        self.assertEqual(account.statement_date, datetime(2023, 1, 31))
        self.assertEqual(account.statement_balance, 1250.75)
    
    def test_category(self):
        """Test Category model."""
        category = Category(
            name="Groceries",
            description="Food and household items",
            tax_related=False,
            income=False,
            expense=True,
            budget_amount=500.0,
            tax_schedule=None
        )
        
        self.assertEqual(category.name, "Groceries")
        self.assertEqual(category.description, "Food and household items")
        self.assertFalse(category.tax_related)
        self.assertFalse(category.income)
        self.assertTrue(category.expense)
        self.assertEqual(category.budget_amount, 500.0)
        self.assertIsNone(category.tax_schedule)
    
    def test_qif_file(self):
        """Test QIFFile model."""
        bank_transactions = [
            BankTransaction(
                date=datetime(2023, 1, 15),
                amount=100.0,
                payee="Grocery Store",
                category="Groceries"
            ),
            BankTransaction(
                date=datetime(2023, 1, 20),
                amount=50.0,
                payee="Gas Station",
                category="Auto:Fuel"
            )
        ]
        
        qif_file = QIFFile(
            type=QIFAccountType.BANK,
            bank_transactions=bank_transactions
        )
        
        self.assertEqual(qif_file.type, QIFAccountType.BANK)
        self.assertEqual(len(qif_file.bank_transactions), 2)
        self.assertEqual(qif_file.bank_transactions[0].payee, "Grocery Store")
        self.assertEqual(qif_file.bank_transactions[1].payee, "Gas Station")
        self.assertIsNone(qif_file.investment_transactions)


class TestCSVModels(unittest.TestCase):
    """Test cases for CSV models."""
    
    def test_csv_bank_transaction(self):
        """Test CSVBankTransaction model."""
        transaction = CSVBankTransaction(
            date=datetime(2023, 1, 15),
            amount=100.0,
            description="Grocery Store",
            reference="1234",
            memo="Weekly shopping",
            category="Groceries",
            account_name="Checking",
            status="*"
        )
        
        self.assertEqual(transaction.date, datetime(2023, 1, 15))
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.description, "Grocery Store")
        self.assertEqual(transaction.reference, "1234")
        self.assertEqual(transaction.memo, "Weekly shopping")
        self.assertEqual(transaction.category, "Groceries")
        self.assertEqual(transaction.account_name, "Checking")
        self.assertEqual(transaction.status, "*")
    
    def test_csv_investment_transaction(self):
        """Test CSVInvestmentTransaction model."""
        transaction = CSVInvestmentTransaction(
            date=datetime(2023, 1, 15),
            action="Buy",
            security="AAPL",
            quantity=10.0,
            price=150.0,
            amount=1500.0,
            commission=7.99,
            description="Buy Apple Inc",
            category=None,
            account="Investment",
            memo="Investment purchase",
            status="*"
        )
        
        self.assertEqual(transaction.date, datetime(2023, 1, 15))
        self.assertEqual(transaction.action, "Buy")
        self.assertEqual(transaction.security, "AAPL")
        self.assertEqual(transaction.quantity, 10.0)
        self.assertEqual(transaction.price, 150.0)
        self.assertEqual(transaction.amount, 1500.0)
        self.assertEqual(transaction.commission, 7.99)
        self.assertEqual(transaction.description, "Buy Apple Inc")
        self.assertIsNone(transaction.category)
        self.assertEqual(transaction.account, "Investment")
        self.assertEqual(transaction.memo, "Investment purchase")
        self.assertEqual(transaction.status, "*")
    
    def test_csv_template(self):
        """Test CSVTemplate model."""
        field_mapping = {
            "Date": "date",
            "Amount": "amount",
            "Description": "payee",
            "Reference": "number",
            "Memo": "memo",
            "Category": "category",
            "Account": "account",
            "Status": "cleared_status"
        }
        
        template = CSVTemplate(
            name="Bank",
            description="Bank account template",
            account_type="Bank",
            field_mapping=field_mapping,
            date_format="%Y-%m-%d",
            delimiter=","
        )
        
        self.assertEqual(template.name, "Bank")
        self.assertEqual(template.description, "Bank account template")
        self.assertEqual(template.account_type, "Bank")
        self.assertEqual(template.field_mapping, field_mapping)
        self.assertEqual(template.date_format, "%Y-%m-%d")
        self.assertEqual(template.delimiter, ",")


if __name__ == "__main__":
    unittest.main()
