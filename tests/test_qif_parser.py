import unittest
import os
import tempfile
from datetime import datetime
from unittest.mock import patch, mock_open

from src.quickenqifimport.parsers.qif_parser import QIFParser
from src.quickenqifimport.models.qif_models import (
    QIFAccountType, QIFClearedStatus, InvestmentAction,
    BankTransaction, CashTransaction, CreditCardTransaction,
    AssetTransaction, LiabilityTransaction, InvestmentTransaction,
    Account, Category, Class, MemorizedTransaction, SplitTransaction,
    QIFFile
)


class TestQIFParser(unittest.TestCase):
    """Test cases for QIF parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = QIFParser()
        
        self.bank_qif = """!Type:Bank
D01/15/2023
T100.00
N1234
PGrocery Store
MWeekly shopping
LGroceries
^
D01/20/2023
T-50.00
PGas Station
LAuto:Fuel
^
"""
        
        self.investment_qif = """!Type:Invst
D01/15/2023
NBUY
YAAPL
I150.00
Q10
T1500.00
MBuy Apple Inc.
^
D01/20/2023
NBUY
YAAPL
I160.00
Q5
T800.00
MSell Apple Inc.
^
"""
        
        self.multi_type_qif = """!Type:Bank
D01/15/2023
T100.00
PGrocery Store
^
!Type:CCard
D01/20/2023
T-50.00
PGas Station
^
"""
        
        self.split_transaction_qif = """!Type:Bank
D01/15/2023
T100.00
PGrocery Store
SGroceries
$60.00
SHousehold
$40.00
^
"""
        
        self.account_qif = """!Account
NChecking
TBank
DMain checking account
/01/15/2023
$1000.00
^
"""
        
        self.category_qif = """!Type:Cat
NGroceries
DFood and household items
EYes
B500.00
^
"""
        
        self.class_qif = """!Type:Class
NPersonal
DPersonal expenses
^
"""
        
        self.memorized_qif = """!Type:Memorized
KPGrocery Store
T100.00
LGroceries
^
"""
        
        self.temp_dir = tempfile.mkdtemp()
        self.bank_file_path = os.path.join(self.temp_dir, "bank.qif")
        self.investment_file_path = os.path.join(self.temp_dir, "investment.qif")
        
        with open(self.bank_file_path, 'w') as file:
            file.write(self.bank_qif)
            
        with open(self.investment_file_path, 'w') as file:
            file.write(self.investment_qif)
    
    def tearDown(self):
        """Tear down test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_parse_file(self):
        """Test parsing a QIF file."""
        qif_file = self.parser.parse_file(self.bank_file_path)
        
        self.assertEqual(qif_file.type, QIFAccountType.BANK)
        self.assertEqual(len(qif_file.bank_transactions), 2)
        
        transaction = qif_file.bank_transactions[0]
        self.assertEqual(transaction.date, datetime(2023, 1, 15))
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.number, "1234")
        self.assertEqual(transaction.payee, "Grocery Store")
        self.assertEqual(transaction.memo, "Weekly shopping")
        self.assertEqual(transaction.category, "Groceries")
        
        transaction = qif_file.bank_transactions[1]
        self.assertEqual(transaction.date, datetime(2023, 1, 20))
        self.assertEqual(transaction.amount, -50.0)
        self.assertEqual(transaction.payee, "Gas Station")
        self.assertEqual(transaction.category, "Auto:Fuel")
    
    def test_parse_investment_file(self):
        """Test parsing an investment QIF file."""
        qif_file = self.parser.parse_file(self.investment_file_path)
        
        self.assertEqual(qif_file.type, QIFAccountType.INVESTMENT)
        self.assertEqual(len(qif_file.investment_transactions), 2)
        
        transaction = qif_file.investment_transactions[0]
        self.assertEqual(transaction.date, datetime(2023, 1, 15))
        self.assertEqual(transaction.action, InvestmentAction.BUY)
        self.assertEqual(transaction.security, "AAPL")
        self.assertEqual(transaction.price, 150.0)
        self.assertEqual(transaction.quantity, 10.0)
        self.assertEqual(transaction.amount, 1500.0)
        self.assertEqual(transaction.memo, "Buy Apple Inc.")
        
        transaction = qif_file.investment_transactions[1]
        self.assertEqual(transaction.date, datetime(2023, 1, 20))
        self.assertEqual(transaction.action, InvestmentAction.BUY)
        self.assertEqual(transaction.security, "AAPL")
        self.assertEqual(transaction.price, 160.0)
        self.assertEqual(transaction.quantity, 5.0)
        self.assertEqual(transaction.amount, 800.0)
        self.assertEqual(transaction.memo, "Sell Apple Inc.")
    
    def test_parse_string(self):
        """Test parsing QIF content from a string."""
        qif_file = self.parser.parse(self.bank_qif)
        
        self.assertEqual(qif_file.type, QIFAccountType.BANK)
        self.assertEqual(len(qif_file.bank_transactions), 2)
    
    def test_parse_multi_type(self):
        """Test parsing QIF content with multiple account types."""
        qif_file = self.parser.parse(self.multi_type_qif)
        
        self.assertEqual(qif_file.type, QIFAccountType.CCARD)
        self.assertEqual(len(qif_file.bank_transactions), 1)
        self.assertEqual(len(qif_file.credit_card_transactions), 1)
        
        bank_transaction = qif_file.bank_transactions[0]
        self.assertEqual(bank_transaction.date, datetime(2023, 1, 15))
        self.assertEqual(bank_transaction.amount, 100.0)
        self.assertEqual(bank_transaction.payee, "Grocery Store")
        
        cc_transaction = qif_file.credit_card_transactions[0]
        self.assertEqual(cc_transaction.date, datetime(2023, 1, 20))
        self.assertEqual(cc_transaction.amount, -50.0)
        self.assertEqual(cc_transaction.payee, "Gas Station")
    
    def test_parse_split_transaction(self):
        """Test parsing a split transaction."""
        qif_file = self.parser.parse(self.split_transaction_qif)
        
        self.assertEqual(qif_file.type, QIFAccountType.BANK)
        self.assertEqual(len(qif_file.bank_transactions), 1)
        
        transaction = qif_file.bank_transactions[0]
        self.assertEqual(transaction.date, datetime(2023, 1, 15))
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.payee, "Grocery Store")
        
        self.assertIsNotNone(transaction.splits)
        self.assertEqual(len(transaction.splits), 2)
        
        split1 = transaction.splits[0]
        self.assertEqual(split1.category, "Groceries")
        self.assertEqual(split1.amount, 60.0)
        
        split2 = transaction.splits[1]
        self.assertEqual(split2.category, "Household")
        self.assertEqual(split2.amount, 40.0)
    
    def test_parse_account(self):
        """Test parsing an account entry."""
        qif_file = self.parser.parse(self.account_qif)
        
        self.assertEqual(qif_file.type, QIFAccountType.ACCOUNT)
        self.assertEqual(len(qif_file.accounts), 1)
        
        account = qif_file.accounts[0]
        self.assertEqual(account.name, "Checking")
        self.assertEqual(account.type, QIFAccountType.BANK)
        self.assertEqual(account.description, "Main checking account")
        self.assertEqual(account.statement_date, datetime(2023, 1, 15))
        self.assertEqual(account.statement_balance, 1000.0)
    
    def test_parse_category(self):
        """Test parsing a category entry."""
        qif_file = self.parser.parse(self.category_qif)
        
        self.assertEqual(qif_file.type, QIFAccountType.CATEGORY)
        self.assertEqual(len(qif_file.categories), 1)
        
        category = qif_file.categories[0]
        self.assertEqual(category.name, "Groceries")
        self.assertEqual(category.description, "Food and household items")
        self.assertIsNone(category.tax_related)
        self.assertIsNotNone(category.expense)
        self.assertEqual(category.budget_amount, 500.0)
    
    def test_parse_class(self):
        """Test parsing a class entry."""
        qif_file = self.parser.parse(self.class_qif)
        
        self.assertEqual(qif_file.type, QIFAccountType.CLASS)
        self.assertEqual(len(qif_file.classes), 1)
        
        cls = qif_file.classes[0]
        self.assertEqual(cls.name, "Personal")
        self.assertEqual(cls.description, "Personal expenses")
    
    def test_parse_memorized(self):
        """Test parsing a memorized transaction entry."""
        memorized_qif_with_date = """!Type:Memorized
KPGrocery Store
D01/15/2023
T100.00
LGroceries
^
"""
        qif_file = self.parser.parse(memorized_qif_with_date)
        
        self.assertEqual(qif_file.type, QIFAccountType.MEMORIZED)
        self.assertEqual(len(qif_file.memorized_transactions), 1)
        
        memorized = qif_file.memorized_transactions[0]
        self.assertIsNotNone(memorized.transaction)
        
        transaction = memorized.transaction
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.category, "Groceries")
    
    def test_parse_date(self):
        """Test parsing dates in various formats."""
        test_cases = [
            ("01/15/23", datetime(2023, 1, 15)),
            ("01/15/2023", datetime(2023, 1, 15)),
            ("15/01/23", datetime(2023, 1, 15)),
            ("15/01/2023", datetime(2023, 1, 15)),
            ("2023-01-15", datetime(2023, 1, 15))
        ]
        
        for date_str, expected in test_cases:
            with self.subTest(date_str=date_str):
                result = self.parser._parse_date(date_str)
                self.assertEqual(result, expected)
    
    def test_parse_amount(self):
        """Test parsing amounts."""
        test_cases = [
            ("100.00", 100.0),
            ("-50.00", -50.0),
            ("1,000.00", 1000.0),
            ("1,234,567.89", 1234567.89)
        ]
        
        for amount_str, expected in test_cases:
            with self.subTest(amount_str=amount_str):
                result = self.parser._parse_amount(amount_str)
                self.assertEqual(result, expected)
    
    def test_parse_cleared_status(self):
        """Test parsing cleared status."""
        test_cases = [
            ("", QIFClearedStatus.UNCLEARED),
            ("*", QIFClearedStatus.CLEARED),
            ("c", QIFClearedStatus.CLEARED_ALT),
            ("X", QIFClearedStatus.RECONCILED),
            ("R", QIFClearedStatus.RECONCILED_ALT),
            ("unknown", QIFClearedStatus.UNCLEARED)
        ]
        
        for status_str, expected in test_cases:
            with self.subTest(status_str=status_str):
                result = self.parser._parse_cleared_status(status_str)
                self.assertEqual(result, expected)
    
    def test_create_field_dict(self):
        """Test creating a field dictionary from QIF entry lines."""
        entry = [
            "D01/15/2023",
            "T100.00",
            "N1234",
            "PGrocery Store",
            "MWeekly shopping",
            "LGroceries",
            "A123 Main St",
            "AAnytown, CA 12345"
        ]
        
        field_dict = self.parser._create_field_dict(entry)
        
        self.assertEqual(field_dict["D"], "01/15/2023")
        self.assertEqual(field_dict["T"], "100.00")
        self.assertEqual(field_dict["N"], "1234")
        self.assertEqual(field_dict["P"], "Grocery Store")
        self.assertEqual(field_dict["M"], "Weekly shopping")
        self.assertEqual(field_dict["L"], "Groceries")
        self.assertEqual(field_dict["A"], ["123 Main St", "Anytown, CA 12345"])
    
    def test_extract_splits(self):
        """Test extracting split transactions."""
        field_dict = {
            "S": ["Groceries", "Household"],
            "$": ["60.00", "40.00"],
            "E": ["Food", "Supplies"],
            "%": ["60", "40"]
        }
        
        splits = self.parser._extract_splits(field_dict)
        
        self.assertEqual(len(splits), 2)
        
        self.assertEqual(splits[0].category, "Groceries")
        self.assertEqual(splits[0].amount, 60.0)
        self.assertEqual(splits[0].memo, "Food")
        self.assertEqual(splits[0].percent, 60.0)
        
        self.assertEqual(splits[1].category, "Household")
        self.assertEqual(splits[1].amount, 40.0)
        self.assertEqual(splits[1].memo, "Supplies")
        self.assertEqual(splits[1].percent, 40.0)
    
    def test_extract_splits_single(self):
        """Test extracting a single split transaction."""
        field_dict = {
            "S": "Groceries",
            "$": "100.00",
            "E": "Food"
        }
        
        splits = self.parser._extract_splits(field_dict)
        
        self.assertEqual(len(splits), 1)
        
        self.assertEqual(splits[0].category, "Groceries")
        self.assertEqual(splits[0].amount, 100.0)
        self.assertEqual(splits[0].memo, "Food")
    
    def test_parse_invalid_qif(self):
        """Test parsing invalid QIF content."""
        invalid_qif = "This is not a valid QIF file"
        
        with self.assertRaises(ValueError):
            self.parser.parse(invalid_qif)
    
    def test_parse_empty_qif(self):
        """Test parsing empty QIF content."""
        with self.assertRaises(ValueError):
            self.parser.parse("")
    
    def test_parse_unknown_header(self):
        """Test parsing QIF with unknown header."""
        unknown_header_qif = "!Type:Unknown\nD01/15/2023\nT100.00\n^"
        
        with self.assertRaises(ValueError):
            self.parser.parse(unknown_header_qif)
    
    def test_parse_invalid_date(self):
        """Test parsing QIF with invalid date."""
        invalid_date_qif = "!Type:Bank\nDnot-a-date\nT100.00\n^"
        
        with self.assertRaises(ValueError):
            self.parser.parse(invalid_date_qif)


if __name__ == "__main__":
    unittest.main()
