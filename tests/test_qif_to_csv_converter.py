import unittest
import os
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.quickenqifimport.converters.qif_to_csv_converter import QIFToCSVConverter
from src.quickenqifimport.models.qif_models import (
    QIFFile, QIFAccountType, QIFClearedStatus, InvestmentAction,
    BankTransaction, CashTransaction, CreditCardTransaction,
    AssetTransaction, LiabilityTransaction, InvestmentTransaction,
    Account, Category, Class, MemorizedTransaction, SplitTransaction
)
from src.quickenqifimport.models.csv_models import CSVTemplate


class TestQIFToCSVConverter(unittest.TestCase):
    """Test cases for QIF to CSV converter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.converter = QIFToCSVConverter()
        self.temp_dir = tempfile.mkdtemp()
        
        self.qif_file_path = os.path.join(self.temp_dir, "test.qif")
        self.csv_output_path = os.path.join(self.temp_dir, "output.csv")
        
        self.bank_transactions = [
            BankTransaction(
                date=datetime(2023, 1, 15),
                amount=100.00,
                payee="Grocery Store",
                number="1234",
                memo="Weekly shopping",
                category="Groceries",
                cleared_status=QIFClearedStatus.CLEARED
            ),
            BankTransaction(
                date=datetime(2023, 1, 20),
                amount=-50.00,
                payee="Gas Station",
                number="5678",
                memo="Fuel",
                category="Auto:Fuel",
                cleared_status=QIFClearedStatus.UNCLEARED
            )
        ]
        
        self.investment_transactions = [
            InvestmentTransaction(
                date=datetime(2023, 1, 15),
                action=InvestmentAction.BUY,
                security="AAPL",
                quantity=10.0,
                price=150.0,
                amount=1500.0,
                commission=10.0,
                text="Buy Apple Inc.",
                memo="Purchase",
                account="Brokerage",
                cleared_status=QIFClearedStatus.CLEARED
            ),
            InvestmentTransaction(
                date=datetime(2023, 1, 20),
                action=InvestmentAction.SELL,
                security="AAPL",
                quantity=5.0,
                price=160.0,
                amount=800.0,
                commission=5.0,
                text="Sell Apple Inc.",
                memo="Sale",
                account="Brokerage",
                cleared_status=QIFClearedStatus.UNCLEARED
            )
        ]
        
        self.accounts = [
            Account(
                name="Checking",
                type=QIFAccountType.BANK,
                description="Primary checking account",
                credit_limit=0.0,
                statement_date=datetime(2023, 1, 31),
                statement_balance=1000.0
            ),
            Account(
                name="Credit Card",
                type=QIFAccountType.CCARD,
                description="Primary credit card",
                credit_limit=5000.0,
                statement_date=datetime(2023, 1, 15),
                statement_balance=-500.0
            )
        ]
        
        self.categories = [
            Category(
                name="Groceries",
                description="Food and household items",
                tax_related=False,
                income=False,
                expense=True,
                budget_amount=500.0,
                tax_schedule="A"
            ),
            Category(
                name="Salary",
                description="Employment income",
                tax_related=True,
                income=True,
                expense=False,
                budget_amount=5000.0,
                tax_schedule="B"
            )
        ]
        
        self.classes = [
            Class(
                name="Personal",
                description="Personal expenses"
            ),
            Class(
                name="Business",
                description="Business expenses"
            )
        ]
        
        self.bank_template = CSVTemplate(
            name="Bank",
            account_type="Bank",
            field_mapping={
                "Date": "date",
                "Amount": "amount",
                "Description": "payee",
                "Reference": "number",
                "Memo": "memo",
                "Category": "category",
                "Status": "cleared_status"
            },
            description="Bank template",
            date_format="%Y-%m-%d",
            delimiter=","
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_convert_bank_transactions(self):
        """Test converting bank transactions to CSV."""
        qif_file = QIFFile(type=QIFAccountType.BANK, bank_transactions=self.bank_transactions)
        csv_content = self.converter.convert(qif_file)
        
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 3)  # Header + 2 transactions
        
        headers = [h.strip() for h in lines[0].split(',')]
        self.assertIn('Date', headers)
        self.assertIn('Amount', headers)
        self.assertIn('Description', headers)
        self.assertIn('Reference', headers)
        self.assertIn('Memo', headers)
        self.assertIn('Category', headers)
        self.assertIn('Status', headers)
        
        first_transaction = lines[1].split(',')
        date_index = headers.index('Date')
        amount_index = headers.index('Amount')
        description_index = headers.index('Description')
        
        self.assertEqual(first_transaction[date_index], '2023-01-15')
        self.assertEqual(float(first_transaction[amount_index]), 100.0)
        self.assertEqual(first_transaction[description_index], 'Grocery Store')
    
    def test_convert_bank_transactions_with_template(self):
        """Test converting bank transactions to CSV with a template."""
        qif_file = QIFFile(type=QIFAccountType.BANK, bank_transactions=self.bank_transactions)
        csv_content = self.converter.convert(qif_file, self.bank_template)
        
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 3)  # Header + 2 transactions
        
        headers = [h.strip() for h in lines[0].split(',')]
        for field in self.bank_template.field_mapping.keys():
            self.assertIn(field, headers)
    
    def test_convert_cash_transactions(self):
        """Test converting cash transactions to CSV."""
        cash_transactions = [
            CashTransaction(**transaction.model_dump())
            for transaction in self.bank_transactions
        ]
        qif_file = QIFFile(type=QIFAccountType.CASH, cash_transactions=cash_transactions)
        csv_content = self.converter.convert(qif_file)
        
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 3)  # Header + 2 transactions
    
    def test_convert_credit_card_transactions(self):
        """Test converting credit card transactions to CSV."""
        credit_card_transactions = [
            CreditCardTransaction(**transaction.model_dump())
            for transaction in self.bank_transactions
        ]
        qif_file = QIFFile(type=QIFAccountType.CCARD, credit_card_transactions=credit_card_transactions)
        csv_content = self.converter.convert(qif_file)
        
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 3)  # Header + 2 transactions
    
    def test_convert_asset_transactions(self):
        """Test converting asset transactions to CSV."""
        asset_transactions = [
            AssetTransaction(**transaction.model_dump())
            for transaction in self.bank_transactions
        ]
        qif_file = QIFFile(type=QIFAccountType.ASSET, asset_transactions=asset_transactions)
        csv_content = self.converter.convert(qif_file)
        
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 3)  # Header + 2 transactions
    
    def test_convert_liability_transactions(self):
        """Test converting liability transactions to CSV."""
        liability_transactions = [
            LiabilityTransaction(**transaction.model_dump())
            for transaction in self.bank_transactions
        ]
        qif_file = QIFFile(type=QIFAccountType.LIABILITY, liability_transactions=liability_transactions)
        csv_content = self.converter.convert(qif_file)
        
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 3)  # Header + 2 transactions
    
    def test_convert_investment_transactions(self):
        """Test converting investment transactions to CSV."""
        qif_file = QIFFile(type=QIFAccountType.INVESTMENT, investment_transactions=self.investment_transactions)
        csv_content = self.converter.convert(qif_file)
        
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 3)  # Header + 2 transactions
        
        headers = [h.strip() for h in lines[0].split(',')]
        self.assertIn('Date', headers)
        self.assertIn('Action', headers)
        self.assertIn('Security', headers)
        self.assertIn('Quantity', headers)
        self.assertIn('Price', headers)
        self.assertIn('Amount', headers)
        self.assertIn('Commission', headers)
        
        first_transaction = lines[1].split(',')
        date_index = headers.index('Date')
        action_index = headers.index('Action')
        security_index = headers.index('Security')
        
        self.assertEqual(first_transaction[date_index], '2023-01-15')
        self.assertEqual(first_transaction[action_index], 'Buy')
        self.assertEqual(first_transaction[security_index], 'AAPL')
    
    def test_convert_accounts(self):
        """Test converting accounts to CSV."""
        qif_file = QIFFile(type=QIFAccountType.ACCOUNT, accounts=self.accounts)
        csv_content = self.converter.convert(qif_file)
        
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 3)  # Header + 2 accounts
        
        headers = [h.strip() for h in lines[0].split(',')]
        self.assertIn('Name', headers)
        self.assertIn('Type', headers)
        self.assertIn('Description', headers)
        self.assertIn('Credit Limit', headers)
        
        first_account = lines[1].split(',')
        name_index = headers.index('Name')
        type_index = headers.index('Type')
        
        self.assertEqual(first_account[name_index], 'Checking')
        self.assertEqual(first_account[type_index], 'Bank')
    
    def test_convert_categories(self):
        """Test converting categories to CSV."""
        qif_file = QIFFile(type=QIFAccountType.CATEGORY, categories=self.categories)
        csv_content = self.converter.convert(qif_file)
        
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 3)  # Header + 2 categories
        
        headers = [h.strip() for h in lines[0].split(',')]
        self.assertIn('Name', headers)
        self.assertIn('Description', headers)
        self.assertIn('Tax Related', headers)
        self.assertIn('Income', headers)
        self.assertIn('Expense', headers)
        
        first_category = lines[1].split(',')
        name_index = headers.index('Name')
        expense_index = headers.index('Expense')
        
        self.assertEqual(first_category[name_index], 'Groceries')
        self.assertEqual(first_category[expense_index], 'Yes')
    
    def test_convert_classes(self):
        """Test converting classes to CSV."""
        qif_file = QIFFile(type=QIFAccountType.CLASS, classes=self.classes)
        csv_content = self.converter.convert(qif_file)
        
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 3)  # Header + 2 classes
        
        headers = [h.strip() for h in lines[0].split(',')]
        self.assertIn('Name', headers)
        self.assertIn('Description', headers)
        
        first_class = [cell.strip() for cell in lines[1].split(',')]
        name_index = headers.index('Name')
        description_index = headers.index('Description')
        
        self.assertEqual(first_class[name_index], 'Personal')
        self.assertEqual(first_class[description_index], 'Personal expenses')
    
    def test_convert_bank_transactions_with_splits(self):
        """Test converting bank transactions with splits to CSV."""
        transaction_with_splits = BankTransaction(
            date=datetime(2023, 1, 25),
            amount=150.00,
            payee="Department Store",
            number="9012",
            memo="Monthly shopping",
            category="Household",
            cleared_status=QIFClearedStatus.CLEARED,
            splits=[
                SplitTransaction(category="Groceries", amount=50.0, memo="Food"),
                SplitTransaction(category="Clothing", amount=75.0, memo="Clothes"),
                SplitTransaction(category="Household", amount=25.0, memo="Supplies")
            ]
        )
        
        transactions = self.bank_transactions + [transaction_with_splits]
        qif_file = QIFFile(type=QIFAccountType.BANK, bank_transactions=transactions)
        csv_content = self.converter.convert(qif_file)
        
        lines = csv_content.strip().split('\n')
        self.assertEqual(len(lines), 4)  # Header + 3 transactions
        
        headers = [h.strip() for h in lines[0].split(',')]
        memo_index = headers.index('Memo')
        
        split_transaction = lines[3].split(',')
        self.assertIn("Split transaction with 3 parts", split_transaction[memo_index])
    
    def test_format_cleared_status(self):
        """Test formatting cleared status for CSV output."""
        self.assertEqual(self.converter._format_cleared_status(QIFClearedStatus.UNCLEARED), "")
        self.assertEqual(self.converter._format_cleared_status(QIFClearedStatus.CLEARED), "Cleared")
        self.assertEqual(self.converter._format_cleared_status(QIFClearedStatus.CLEARED_ALT), "Cleared")
        self.assertEqual(self.converter._format_cleared_status(QIFClearedStatus.RECONCILED), "Reconciled")
        self.assertEqual(self.converter._format_cleared_status(QIFClearedStatus.RECONCILED_ALT), "Reconciled")
    
    @patch('src.quickenqifimport.parsers.qif_parser.QIFParser')
    def test_convert_file(self, mock_parser_class):
        """Test converting a QIF file to CSV."""
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        
        qif_file = QIFFile(type=QIFAccountType.BANK, bank_transactions=self.bank_transactions)
        mock_parser.parse_file.return_value = qif_file
        
        self.converter.convert_file(self.qif_file_path, self.csv_output_path)
        
        mock_parser_class.assert_called_once()
        mock_parser.parse_file.assert_called_once_with(self.qif_file_path)
        
        self.assertTrue(os.path.exists(self.csv_output_path))
    
    @patch('src.quickenqifimport.parsers.qif_parser.QIFParser')
    def test_convert_file_with_template(self, mock_parser_class):
        """Test converting a QIF file to CSV with a template."""
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        
        qif_file = QIFFile(type=QIFAccountType.BANK, bank_transactions=self.bank_transactions)
        mock_parser.parse_file.return_value = qif_file
        
        self.converter.convert_file(self.qif_file_path, self.csv_output_path, self.bank_template)
        
        mock_parser_class.assert_called_once()
        mock_parser.parse_file.assert_called_once_with(self.qif_file_path)
        
        self.assertTrue(os.path.exists(self.csv_output_path))
    
    def test_convert_no_data(self):
        """Test converting a QIF file with no data."""
        qif_file = QIFFile(type=QIFAccountType.BANK)
        
        with self.assertRaises(ValueError):
            self.converter.convert(qif_file)


if __name__ == "__main__":
    unittest.main()
