import unittest
from datetime import datetime
import os
import tempfile
from io import StringIO

from src.quickenqifimport.models.qif_models import (
    QIFAccountType, QIFClearedStatus, InvestmentAction,
    BankTransaction, InvestmentTransaction, QIFFile
)
from src.quickenqifimport.parsers.qif_parser import QIFParser
from src.quickenqifimport.parsers.csv_parser import CSVParser
from src.quickenqifimport.models.csv_models import CSVTemplate


class TestQIFParser(unittest.TestCase):
    """Test cases for QIF parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = QIFParser()
        
        self.bank_qif_content = """!Type:Bank
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
        
        self.investment_qif_content = """!Type:Invst
D01/15/2023
NBuy
YAAPL
I150.00
Q10.0
T1500.00
PBuy Apple Inc
MInvestment purchase
O7.99
^
D01/20/2023
NSell
YAAPL
I160.00
Q5.0
T800.00
PSell Apple Inc
MInvestment sale
O7.99
^
"""
        
        self.mixed_qif_content = """!Type:Bank
D01/15/2023
T100.00
PGrocery Store
LGroceries
^
!Type:Invst
D01/15/2023
NBuy
YAAPL
I150.00
Q10.0
T1500.00
^
"""
    
    def test_parse_bank_transactions(self):
        """Test parsing bank transactions."""
        qif_file = self.parser.parse(self.bank_qif_content)
        
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
    
    def test_parse_investment_transactions(self):
        """Test parsing investment transactions."""
        qif_file = self.parser.parse(self.investment_qif_content)
        
        self.assertEqual(qif_file.type, QIFAccountType.INVESTMENT)
        self.assertEqual(len(qif_file.investment_transactions), 2)
        
        transaction = qif_file.investment_transactions[0]
        self.assertEqual(transaction.date, datetime(2023, 1, 15))
        self.assertEqual(transaction.action, InvestmentAction.BUY)
        self.assertEqual(transaction.security, "AAPL")
        self.assertEqual(transaction.price, 150.0)
        self.assertEqual(transaction.quantity, 10.0)
        self.assertEqual(transaction.amount, 1500.0)
        self.assertEqual(transaction.text, "Buy Apple Inc")
        self.assertEqual(transaction.memo, "Investment purchase")
        self.assertEqual(transaction.commission, 7.99)
        
        transaction = qif_file.investment_transactions[1]
        self.assertEqual(transaction.date, datetime(2023, 1, 20))
        self.assertEqual(transaction.action, InvestmentAction.SELL)
        self.assertEqual(transaction.security, "AAPL")
        self.assertEqual(transaction.price, 160.0)
        self.assertEqual(transaction.quantity, 5.0)
        self.assertEqual(transaction.amount, 800.0)
        self.assertEqual(transaction.text, "Sell Apple Inc")
        self.assertEqual(transaction.memo, "Investment sale")
        self.assertEqual(transaction.commission, 7.99)
    
    def test_parse_mixed_transactions(self):
        """Test parsing mixed transaction types."""
        qif_file = self.parser.parse(self.mixed_qif_content)
        
        self.assertEqual(qif_file.type, QIFAccountType.INVESTMENT)
        
        self.assertEqual(len(qif_file.bank_transactions), 1)
        transaction = qif_file.bank_transactions[0]
        self.assertEqual(transaction.date, datetime(2023, 1, 15))
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.payee, "Grocery Store")
        self.assertEqual(transaction.category, "Groceries")
        
        self.assertEqual(len(qif_file.investment_transactions), 1)
        transaction = qif_file.investment_transactions[0]
        self.assertEqual(transaction.date, datetime(2023, 1, 15))
        self.assertEqual(transaction.action, InvestmentAction.BUY)
        self.assertEqual(transaction.security, "AAPL")
        self.assertEqual(transaction.price, 150.0)
        self.assertEqual(transaction.quantity, 10.0)
        self.assertEqual(transaction.amount, 1500.0)
    
    def test_parse_file(self):
        """Test parsing from a file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(self.bank_qif_content)
            temp_file_path = temp_file.name
        
        try:
            qif_file = self.parser.parse_file(temp_file_path)
            
            self.assertEqual(qif_file.type, QIFAccountType.BANK)
            self.assertEqual(len(qif_file.bank_transactions), 2)
        finally:
            os.unlink(temp_file_path)
    
    def test_parse_invalid_qif(self):
        """Test parsing invalid QIF content."""
        invalid_qif = """D01/15/2023
T100.00
PGrocery Store
^
"""
        with self.assertRaises(ValueError):
            self.parser.parse(invalid_qif)
        
        with self.assertRaises(ValueError):
            self.parser.parse("")
        
        invalid_header_qif = """!Type:Invalid
D01/15/2023
T100.00
^
"""
        with self.assertRaises(ValueError):
            self.parser.parse(invalid_header_qif)


class TestCSVParser(unittest.TestCase):
    """Test cases for CSV parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = CSVParser()
        
        self.bank_csv_content = """Date,Amount,Description,Reference,Memo,Category,Account,Status
2023-01-15,100.00,Grocery Store,1234,Weekly shopping,Groceries,Checking,*
2023-01-20,-50.00,Gas Station,,Fuel purchase,Auto:Fuel,Checking,
"""
        
        self.investment_csv_content = """Date,Action,Security,Quantity,Price,Amount,Commission,Description,Category,Account,Memo,Status
2023-01-15,Buy,AAPL,10.0,150.00,1500.00,7.99,Buy Apple Inc,,Investment,Investment purchase,*
2023-01-20,Sell,AAPL,5.0,160.00,800.00,7.99,Sell Apple Inc,,Investment,Investment sale,
"""
        
        self.bank_template = CSVTemplate(
            name="Bank",
            description="Bank account template",
            account_type="Bank",
            field_mapping={
                "Date": "date",
                "Amount": "amount",
                "Description": "payee",
                "Reference": "number",
                "Memo": "memo",
                "Category": "category",
                "Account": "account",
                "Status": "cleared_status"
            },
            date_format="%Y-%m-%d",
            delimiter=","
        )
    
    def test_parse_bank_csv(self):
        """Test parsing bank CSV content."""
        rows = self.parser.parse(StringIO(self.bank_csv_content))
        
        self.assertEqual(len(rows), 2)
        
        row = rows[0]
        self.assertEqual(row["Date"], "2023-01-15")
        self.assertEqual(row["Amount"], "100.00")
        self.assertEqual(row["Description"], "Grocery Store")
        self.assertEqual(row["Reference"], "1234")
        self.assertEqual(row["Memo"], "Weekly shopping")
        self.assertEqual(row["Category"], "Groceries")
        self.assertEqual(row["Account"], "Checking")
        self.assertEqual(row["Status"], "*")
        
        row = rows[1]
        self.assertEqual(row["Date"], "2023-01-20")
        self.assertEqual(row["Amount"], "-50.00")
        self.assertEqual(row["Description"], "Gas Station")
        self.assertEqual(row["Reference"], "")
        self.assertEqual(row["Memo"], "Fuel purchase")
        self.assertEqual(row["Category"], "Auto:Fuel")
        self.assertEqual(row["Account"], "Checking")
        self.assertEqual(row["Status"], "")
    
    def test_parse_investment_csv(self):
        """Test parsing investment CSV content."""
        rows = self.parser.parse(StringIO(self.investment_csv_content))
        
        self.assertEqual(len(rows), 2)
        
        row = rows[0]
        self.assertEqual(row["Date"], "2023-01-15")
        self.assertEqual(row["Action"], "Buy")
        self.assertEqual(row["Security"], "AAPL")
        self.assertEqual(row["Quantity"], "10.0")
        self.assertEqual(row["Price"], "150.00")
        self.assertEqual(row["Amount"], "1500.00")
        self.assertEqual(row["Commission"], "7.99")
        self.assertEqual(row["Description"], "Buy Apple Inc")
        self.assertEqual(row["Category"], "")
        self.assertEqual(row["Account"], "Investment")
        self.assertEqual(row["Memo"], "Investment purchase")
        self.assertEqual(row["Status"], "*")
    
    def test_parse_with_template(self):
        """Test parsing with a template."""
        rows = self.parser.parse(StringIO(self.bank_csv_content), self.bank_template)
        
        self.assertEqual(len(rows), 2)
        
        row = rows[0]
        self.assertEqual(row["date"], "2023-01-15")
        self.assertEqual(row["amount"], "100.00")
        self.assertEqual(row["payee"], "Grocery Store")
        self.assertEqual(row["number"], "1234")
        self.assertEqual(row["memo"], "Weekly shopping")
        self.assertEqual(row["category"], "Groceries")
        self.assertEqual(row["account"], "Checking")
        self.assertEqual(row["cleared_status"], "*")
    
    def test_parse_bank_transactions(self):
        """Test parsing bank transactions."""
        transactions = self.parser.parse_bank_transactions(StringIO(self.bank_csv_content))
        
        self.assertEqual(len(transactions), 2)
        
        transaction = transactions[0]
        self.assertEqual(transaction.date, datetime(2023, 1, 15))
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.description, "Grocery Store")
        self.assertEqual(transaction.reference, "1234")
        self.assertEqual(transaction.memo, "Weekly shopping")
        self.assertEqual(transaction.category, "Groceries")
        self.assertEqual(transaction.account_name, "Checking")
        self.assertEqual(transaction.status, "*")
        
        transaction = transactions[1]
        self.assertEqual(transaction.date, datetime(2023, 1, 20))
        self.assertEqual(transaction.amount, -50.0)
        self.assertEqual(transaction.description, "Gas Station")
        self.assertEqual(transaction.reference, "")
        self.assertEqual(transaction.memo, "Fuel purchase")
        self.assertEqual(transaction.category, "Auto:Fuel")
        self.assertEqual(transaction.account_name, "Checking")
        self.assertEqual(transaction.status, "")
    
    def test_parse_investment_transactions(self):
        """Test parsing investment transactions."""
        transactions = self.parser.parse_investment_transactions(StringIO(self.investment_csv_content))
        
        self.assertEqual(len(transactions), 2)
        
        transaction = transactions[0]
        self.assertEqual(transaction.date, datetime(2023, 1, 15))
        self.assertEqual(transaction.action, "Buy")
        self.assertEqual(transaction.security, "AAPL")
        self.assertEqual(transaction.quantity, 10.0)
        self.assertEqual(transaction.price, 150.0)
        self.assertEqual(transaction.amount, 1500.0)
        self.assertEqual(transaction.commission, 7.99)
        self.assertEqual(transaction.description, "Buy Apple Inc")
        self.assertEqual(transaction.category, "")
        self.assertEqual(transaction.account, "Investment")
        self.assertEqual(transaction.memo, "Investment purchase")
        self.assertEqual(transaction.status, "*")
    
    def test_detect_template(self):
        """Test template detection."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as bank_file:
            bank_file.write(self.bank_csv_content)
            bank_file_path = bank_file.name
            
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as investment_file:
            investment_file.write(self.investment_csv_content)
            investment_file_path = investment_file.name
        
        try:
            bank_template = self.parser.detect_template(bank_file_path)
            investment_template = self.parser.detect_template(investment_file_path)
            
            self.assertEqual(bank_template, "bank")
            self.assertEqual(investment_template, "investment")
        finally:
            os.unlink(bank_file_path)
            os.unlink(investment_file_path)


if __name__ == "__main__":
    unittest.main()
