import unittest
import os
import tempfile
import csv
from datetime import datetime
from unittest.mock import patch, mock_open

from src.quickenqifimport.parsers.csv_parser import CSVParser
from src.quickenqifimport.models.csv_models import CSVBankTransaction, CSVInvestmentTransaction, CSVTemplate


class TestCSVParser(unittest.TestCase):
    """Test cases for CSV parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = CSVParser()
        
        self.bank_csv = """Date,Amount,Description,Reference,Memo,Category,Account,Status
2023-01-15,100.00,Grocery Store,1234,Weekly shopping,Groceries,Checking,*
2023-01-20,-50.00,Gas Station,5678,Fuel,Auto:Fuel,Checking,
"""
        
        self.investment_csv = """Date,Action,Security,Quantity,Price,Amount,Commission,Description,Category,Account,Memo,Status
2023-01-15,Buy,AAPL,10,150.00,1500.00,10.00,Buy Apple Inc.,Investments,Brokerage,Purchase,*
2023-01-20,Sell,AAPL,5,160.00,800.00,5.00,Sell Apple Inc.,Investments,Brokerage,Sale,
"""
        
        self.temp_dir = tempfile.mkdtemp()
        self.bank_file_path = os.path.join(self.temp_dir, "bank.csv")
        self.investment_file_path = os.path.join(self.temp_dir, "investment.csv")
        
        with open(self.bank_file_path, 'w') as file:
            file.write(self.bank_csv)
            
        with open(self.investment_file_path, 'w') as file:
            file.write(self.investment_csv)
        
        self.bank_template = CSVTemplate(
            name="Bank",
            account_type="Bank",
            field_mapping={
                "Date": "date",
                "Amount": "amount",
                "Description": "description",
                "Reference": "reference",
                "Memo": "memo",
                "Category": "category",
                "Account": "account_name",
                "Status": "status"
            },
            description="Bank template",
            date_format="%Y-%m-%d",
            delimiter=","
        )
        
        self.investment_template = CSVTemplate(
            name="Investment",
            account_type="Investment",
            field_mapping={
                "Date": "date",
                "Action": "action",
                "Security": "security",
                "Quantity": "quantity",
                "Price": "price",
                "Amount": "amount",
                "Commission": "commission",
                "Description": "description",
                "Category": "category",
                "Account": "account",
                "Memo": "memo",
                "Status": "status"
            },
            description="Investment template",
            date_format="%Y-%m-%d",
            delimiter=","
        )
    
    def tearDown(self):
        """Tear down test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_parse_file(self):
        """Test parsing a CSV file."""
        rows = self.parser.parse_file(self.bank_file_path)
        
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
        self.assertEqual(row["Reference"], "5678")
        self.assertEqual(row["Memo"], "Fuel")
        self.assertEqual(row["Category"], "Auto:Fuel")
        self.assertEqual(row["Account"], "Checking")
        self.assertEqual(row["Status"], "")
    
    def test_parse_file_with_template(self):
        """Test parsing a CSV file with a template."""
        rows = self.parser.parse_file(self.bank_file_path, self.bank_template)
        
        self.assertEqual(len(rows), 2)
        
        row = rows[0]
        self.assertEqual(row["date"], "2023-01-15")
        self.assertEqual(row["amount"], "100.00")
        self.assertEqual(row["description"], "Grocery Store")
        self.assertEqual(row["reference"], "1234")
        self.assertEqual(row["memo"], "Weekly shopping")
        self.assertEqual(row["category"], "Groceries")
        self.assertEqual(row["account_name"], "Checking")
        self.assertEqual(row["status"], "*")
    
    def test_parse_string(self):
        """Test parsing CSV content from a string."""
        rows = self.parser.parse(self.bank_csv)
        
        self.assertEqual(len(rows), 2)
        
        row = rows[0]
        self.assertEqual(row["Date"], "2023-01-15")
        self.assertEqual(row["Amount"], "100.00")
        self.assertEqual(row["Description"], "Grocery Store")
    
    def test_parse_bank_transactions(self):
        """Test parsing bank transactions."""
        transactions = self.parser.parse_bank_transactions(self.bank_file_path)
        
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
        self.assertEqual(transaction.reference, "5678")
        self.assertEqual(transaction.memo, "Fuel")
        self.assertEqual(transaction.category, "Auto:Fuel")
        self.assertEqual(transaction.account_name, "Checking")
        self.assertEqual(transaction.status, "")
    
    def test_parse_bank_transactions_with_template(self):
        """Test parsing bank transactions with a template."""
        transactions = self.parser.parse_bank_transactions(self.bank_file_path, self.bank_template)
        
        self.assertEqual(len(transactions), 2)
        
        transaction = transactions[0]
        self.assertEqual(transaction.date, datetime(2023, 1, 15))
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.description, "Grocery Store")
    
    def test_parse_investment_transactions(self):
        """Test parsing investment transactions."""
        transactions = self.parser.parse_investment_transactions(self.investment_file_path)
        
        self.assertEqual(len(transactions), 2)
        
        transaction = transactions[0]
        self.assertEqual(transaction.date, datetime(2023, 1, 15))
        self.assertEqual(transaction.action, "Buy")
        self.assertEqual(transaction.security, "AAPL")
        self.assertEqual(transaction.quantity, 10.0)
        self.assertEqual(transaction.price, 150.0)
        self.assertEqual(transaction.amount, 1500.0)
        self.assertEqual(transaction.commission, 10.0)
        self.assertEqual(transaction.description, "Buy Apple Inc.")
        self.assertEqual(transaction.category, "Investments")
        self.assertEqual(transaction.account, "Brokerage")
        self.assertEqual(transaction.memo, "Purchase")
        self.assertEqual(transaction.status, "*")
        
        transaction = transactions[1]
        self.assertEqual(transaction.date, datetime(2023, 1, 20))
        self.assertEqual(transaction.action, "Sell")
        self.assertEqual(transaction.security, "AAPL")
        self.assertEqual(transaction.quantity, 5.0)
        self.assertEqual(transaction.price, 160.0)
        self.assertEqual(transaction.amount, 800.0)
        self.assertEqual(transaction.commission, 5.0)
        self.assertEqual(transaction.description, "Sell Apple Inc.")
        self.assertEqual(transaction.category, "Investments")
        self.assertEqual(transaction.account, "Brokerage")
        self.assertEqual(transaction.memo, "Sale")
        self.assertEqual(transaction.status, "")
    
    def test_parse_investment_transactions_with_template(self):
        """Test parsing investment transactions with a template."""
        transactions = self.parser.parse_investment_transactions(self.investment_file_path, self.investment_template)
        
        self.assertEqual(len(transactions), 2)
        
        transaction = transactions[0]
        self.assertEqual(transaction.date, datetime(2023, 1, 15))
        self.assertEqual(transaction.action, "Buy")
        self.assertEqual(transaction.security, "AAPL")
    
    def test_detect_template(self):
        """Test detecting template type."""
        template_type = self.parser.detect_template(self.bank_file_path)
        self.assertEqual(template_type, "bank")
        
        template_type = self.parser.detect_template(self.investment_file_path)
        self.assertEqual(template_type, "investment")
        
        unknown_file_path = os.path.join(self.temp_dir, "unknown.csv")
        with open(unknown_file_path, 'w') as file:
            file.write("Column1,Column2,Column3\n1,2,3\n")
            
        template_type = self.parser.detect_template(unknown_file_path)
        self.assertIsNone(template_type)
    
    def test_parse_bank_transactions_with_invalid_date(self):
        """Test parsing bank transactions with invalid date."""
        invalid_date_csv = """Date,Amount,Description
invalid-date,100.00,Test
"""
        invalid_file_path = os.path.join(self.temp_dir, "invalid_date.csv")
        with open(invalid_file_path, 'w') as file:
            file.write(invalid_date_csv)
            
        with patch('builtins.print') as mock_print:
            transactions = self.parser.parse_bank_transactions(invalid_file_path)
            
            self.assertEqual(len(transactions), 0)
            mock_print.assert_called_once()
    
    def test_parse_bank_transactions_with_missing_date(self):
        """Test parsing bank transactions with missing date."""
        missing_date_csv = """Date,Amount,Description
,100.00,Test
"""
        missing_file_path = os.path.join(self.temp_dir, "missing_date.csv")
        with open(missing_file_path, 'w') as file:
            file.write(missing_date_csv)
            
        with patch('builtins.print') as mock_print:
            transactions = self.parser.parse_bank_transactions(missing_file_path)
            
            self.assertEqual(len(transactions), 0)
            mock_print.assert_called_once()
    
    def test_parse_investment_transactions_with_invalid_date(self):
        """Test parsing investment transactions with invalid date."""
        invalid_date_csv = """Date,Action,Security,Quantity,Price,Amount
invalid-date,Buy,AAPL,10,150.00,1500.00
"""
        invalid_file_path = os.path.join(self.temp_dir, "invalid_date_inv.csv")
        with open(invalid_file_path, 'w') as file:
            file.write(invalid_date_csv)
            
        with patch('builtins.print') as mock_print:
            transactions = self.parser.parse_investment_transactions(invalid_file_path)
            
            self.assertEqual(len(transactions), 0)
            mock_print.assert_called_once()
    
    def test_parse_investment_transactions_with_missing_date(self):
        """Test parsing investment transactions with missing date."""
        missing_date_csv = """Date,Action,Security,Quantity,Price,Amount
,Buy,AAPL,10,150.00,1500.00
"""
        missing_file_path = os.path.join(self.temp_dir, "missing_date_inv.csv")
        with open(missing_file_path, 'w') as file:
            file.write(missing_date_csv)
            
        with patch('builtins.print') as mock_print:
            transactions = self.parser.parse_investment_transactions(missing_file_path)
            
            self.assertEqual(len(transactions), 0)
            mock_print.assert_called_once()
    
    def test_parse_with_different_delimiter(self):
        """Test parsing CSV with different delimiter."""
        semicolon_csv = """Date;Amount;Description
2023-01-15;100.00;Grocery Store
"""
        semicolon_file_path = os.path.join(self.temp_dir, "semicolon.csv")
        with open(semicolon_file_path, 'w') as file:
            file.write(semicolon_csv)
            
        parser = CSVParser(delimiter=";")
        rows = parser.parse_file(semicolon_file_path)
        
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Date"], "2023-01-15")
        self.assertEqual(rows[0]["Amount"], "100.00")
        self.assertEqual(rows[0]["Description"], "Grocery Store")
    
    def test_parse_with_different_date_format(self):
        """Test parsing CSV with different date format."""
        different_date_csv = """Date,Amount,Description
01/15/2023,100.00,Grocery Store
"""
        date_file_path = os.path.join(self.temp_dir, "different_date.csv")
        with open(date_file_path, 'w') as file:
            file.write(different_date_csv)
            
        parser = CSVParser(date_format="%m/%d/%Y")
        transactions = parser.parse_bank_transactions(date_file_path)
        
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].date, datetime(2023, 1, 15))


if __name__ == "__main__":
    unittest.main()
