import unittest
from datetime import datetime
import os
import tempfile
from io import StringIO

from src.quickenqifimport.models.qif_models import (
    QIFAccountType, QIFClearedStatus, InvestmentAction,
    BankTransaction, InvestmentTransaction, QIFFile
)
from src.quickenqifimport.models.csv_models import (
    CSVBankTransaction, CSVInvestmentTransaction, CSVTemplate
)
from src.quickenqifimport.converters.qif_to_csv_converter import QIFToCSVConverter
from src.quickenqifimport.converters.csv_to_qif_converter import CSVToQIFConverter
from src.quickenqifimport.parsers.qif_parser import QIFParser
from src.quickenqifimport.parsers.csv_parser import CSVParser


class TestQIFToCSVConverter(unittest.TestCase):
    """Test cases for QIF to CSV converter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.converter = QIFToCSVConverter()
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
    
    def test_convert_bank_transactions(self):
        """Test converting bank transactions to CSV."""
        qif_file = self.parser.parse(self.bank_qif_content)
        
        csv_content = self.converter.convert(qif_file)
        
        self.assertIn("Date,Amount,Description,Reference,Memo,Category,Status", csv_content)
        self.assertIn("2023-01-15,100.0,Grocery Store,1234,Weekly shopping,Groceries,", csv_content)
        self.assertIn("2023-01-20,-50.0,Gas Station,,,Auto:Fuel,", csv_content)
    
    def test_convert_investment_transactions(self):
        """Test converting investment transactions to CSV."""
        qif_file = self.parser.parse(self.investment_qif_content)
        
        csv_content = self.converter.convert(qif_file)
        
        self.assertIn("Date,Action,Security,Quantity,Price,Amount,Commission,Description,Memo,Account,Status", csv_content)
        self.assertIn("2023-01-15,Buy,AAPL,10.0,150.0,1500.0,7.99,Buy Apple Inc,Investment purchase,", csv_content)
        self.assertIn("2023-01-20,Sell,AAPL,5.0,160.0,800.0,7.99,Sell Apple Inc,Investment sale,", csv_content)
    
    def test_convert_with_template(self):
        """Test converting with a template."""
        qif_file = self.parser.parse(self.bank_qif_content)
        
        csv_content = self.converter.convert(qif_file, self.bank_template)
        
        self.assertIn("Date,Amount,Description,Reference,Memo,Category,Account,Status", csv_content)
        self.assertIn("2023-01-15,100.0,Grocery Store,1234,Weekly shopping,Groceries,,", csv_content)
        self.assertIn("2023-01-20,-50.0,Gas Station,,,Auto:Fuel,,", csv_content)
    
    def test_convert_file(self):
        """Test converting from a file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as qif_file:
            qif_file.write(self.bank_qif_content)
            qif_file_path = qif_file.name
            
        csv_file_path = tempfile.mktemp(suffix='.csv')
        
        try:
            self.converter.convert_file(qif_file_path, csv_file_path)
            
            self.assertTrue(os.path.exists(csv_file_path))
            
            with open(csv_file_path, 'r') as file:
                csv_content = file.read()
                self.assertIn("Date,Amount,Description,Reference,Memo,Category,Status", csv_content)
                self.assertIn("2023-01-15,100.0,Grocery Store,1234,Weekly shopping,Groceries,", csv_content)
                self.assertIn("2023-01-20,-50.0,Gas Station,,,Auto:Fuel,", csv_content)
        finally:
            os.unlink(qif_file_path)
            if os.path.exists(csv_file_path):
                os.unlink(csv_file_path)
    
    def test_custom_date_format(self):
        """Test custom date format."""
        qif_file = self.parser.parse(self.bank_qif_content)
        
        self.converter.date_format = "%d-%m-%Y"
        
        csv_content = self.converter.convert(qif_file)
        
        self.assertIn("15-01-2023,100.0,Grocery Store", csv_content)
        self.assertIn("20-01-2023,-50.0,Gas Station", csv_content)
    
    def test_custom_delimiter(self):
        """Test custom delimiter."""
        qif_file = self.parser.parse(self.bank_qif_content)
        
        self.converter.delimiter = ";"
        
        csv_content = self.converter.convert(qif_file)
        
        self.assertIn("Date;Amount;Description;Reference;Memo;Category;Status", csv_content)
        self.assertIn("2023-01-15;100.0;Grocery Store;1234;Weekly shopping;Groceries;", csv_content)
        self.assertIn("2023-01-20;-50.0;Gas Station;;;Auto:Fuel;", csv_content)


class TestCSVToQIFConverter(unittest.TestCase):
    """Test cases for CSV to QIF converter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.converter = CSVToQIFConverter()
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
    
    def test_convert_bank_transactions(self):
        """Test converting bank transactions to QIF."""
        transactions = self.parser.parse_bank_transactions(StringIO(self.bank_csv_content))
        
        qif_content = self.converter.convert_bank_transactions(transactions)
        
        self.assertIn("!Type:Bank", qif_content)
        self.assertIn("D01/15/2023", qif_content)
        self.assertIn("T100.00", qif_content)
        self.assertIn("N1234", qif_content)
        self.assertIn("PGrocery Store", qif_content)
        self.assertIn("MWeekly shopping", qif_content)
        self.assertIn("LGroceries", qif_content)
        self.assertIn("C*", qif_content)
        self.assertIn("D01/20/2023", qif_content)
        self.assertIn("T-50.00", qif_content)
        self.assertIn("PGas Station", qif_content)
        self.assertIn("MFuel purchase", qif_content)
        self.assertIn("LAuto:Fuel", qif_content)
    
    def test_convert_investment_transactions(self):
        """Test converting investment transactions to QIF."""
        transactions = self.parser.parse_investment_transactions(StringIO(self.investment_csv_content))
        
        qif_content = self.converter.convert_investment_transactions(transactions)
        
        self.assertIn("!Type:Invst", qif_content)
        self.assertIn("D01/15/2023", qif_content)
        self.assertIn("NBuy", qif_content)
        self.assertIn("YAAPL", qif_content)
        self.assertIn("I150.00", qif_content)
        self.assertIn("Q10.0", qif_content)
        self.assertIn("T1500.00", qif_content)
        self.assertIn("PBuy Apple Inc", qif_content)
        self.assertIn("MInvestment purchase", qif_content)
        self.assertIn("O7.99", qif_content)
        self.assertIn("C*", qif_content)
    
    def test_convert_with_template(self):
        """Test converting with a template."""
        rows = self.parser.parse(StringIO(self.bank_csv_content), self.bank_template)
        
        qif_content = self.converter.convert_generic(rows, QIFAccountType.BANK)
        
        self.assertIn("!Type:Bank", qif_content)
        self.assertIn("N", qif_content)
        self.assertIn("D", qif_content)
    
    def test_convert_file(self):
        """Test converting from a file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as csv_file:
            csv_file.write(self.bank_csv_content)
            csv_file_path = csv_file.name
            
        qif_file_path = tempfile.mktemp(suffix='.qif')
        
        try:
            self.converter.convert_file(csv_file_path, qif_file_path, QIFAccountType.BANK)
            
            self.assertTrue(os.path.exists(qif_file_path))
            
            with open(qif_file_path, 'r') as file:
                qif_content = file.read()
                self.assertIn("!Type:Bank", qif_content)
                self.assertIn("D01/15/2023", qif_content)
                self.assertIn("T100.00", qif_content)
                self.assertIn("N1234", qif_content)
                self.assertIn("PGrocery Store", qif_content)
        finally:
            os.unlink(csv_file_path)
            if os.path.exists(qif_file_path):
                os.unlink(qif_file_path)
    
    def test_custom_date_format(self):
        """Test custom date format."""
        self.converter.date_format = "%d-%m-%Y"
        
        custom_csv_content = """Date,Amount,Description,Reference,Memo,Category,Account,Status
15-01-2023,100.00,Grocery Store,1234,Weekly shopping,Groceries,Checking,*
20-01-2023,-50.00,Gas Station,,Fuel purchase,Auto:Fuel,Checking,
"""
        
        transactions = self.parser.parse_bank_transactions(StringIO(custom_csv_content))
        
        qif_content = self.converter.convert_bank_transactions(transactions)
        
        self.assertIn("D01/15/2023", qif_content)
        self.assertIn("D01/20/2023", qif_content)
    
    def test_parse_cleared_status(self):
        """Test parsing cleared status."""
        self.assertEqual(self.converter._parse_cleared_status("cleared"), "*")
        self.assertEqual(self.converter._parse_cleared_status("c"), "*")
        self.assertEqual(self.converter._parse_cleared_status("*"), "*")
        self.assertEqual(self.converter._parse_cleared_status("reconciled"), "X")
        self.assertEqual(self.converter._parse_cleared_status("r"), "X")
        self.assertEqual(self.converter._parse_cleared_status("x"), "X")
        self.assertEqual(self.converter._parse_cleared_status(""), "")
        self.assertEqual(self.converter._parse_cleared_status(None), "")


if __name__ == "__main__":
    unittest.main()
