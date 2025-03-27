import unittest
import os
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.quickenqifimport.converters.csv_to_qif_converter import CSVToQIFConverter
from src.quickenqifimport.models.qif_models import QIFAccountType
from src.quickenqifimport.models.csv_models import CSVBankTransaction, CSVInvestmentTransaction, CSVTemplate


class TestCSVToQIFConverter(unittest.TestCase):
    """Test cases for CSV to QIF converter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.converter = CSVToQIFConverter()
        self.temp_dir = tempfile.mkdtemp()
        
        self.bank_csv_path = os.path.join(self.temp_dir, "bank.csv")
        self.investment_csv_path = os.path.join(self.temp_dir, "investment.csv")
        self.qif_output_path = os.path.join(self.temp_dir, "output.qif")
        
        self.bank_transactions = [
            CSVBankTransaction(
                date=datetime(2023, 1, 15),
                amount=100.00,
                description="Grocery Store",
                reference="1234",
                memo="Weekly shopping",
                category="Groceries",
                account_name="Checking",
                status="*"
            ),
            CSVBankTransaction(
                date=datetime(2023, 1, 20),
                amount=-50.00,
                description="Gas Station",
                reference="5678",
                memo="Fuel",
                category="Auto:Fuel",
                account_name="Checking",
                status=""
            )
        ]
        
        self.investment_transactions = [
            CSVInvestmentTransaction(
                date=datetime(2023, 1, 15),
                action="Buy",
                security="AAPL",
                quantity=10.0,
                price=150.0,
                amount=1500.0,
                commission=10.0,
                description="Buy Apple Inc.",
                category="Investments",
                account="Brokerage",
                memo="Purchase",
                status="*"
            ),
            CSVInvestmentTransaction(
                date=datetime(2023, 1, 20),
                action="Sell",
                security="AAPL",
                quantity=5.0,
                price=160.0,
                amount=800.0,
                commission=5.0,
                description="Sell Apple Inc.",
                category="Investments",
                account="Brokerage",
                memo="Sale",
                status=""
            )
        ]
        
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
    
    def tearDown(self):
        """Tear down test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_convert_bank_transactions(self):
        """Test converting bank transactions to QIF format."""
        qif_content = self.converter.convert_bank_transactions(self.bank_transactions)
        
        expected_lines = [
            "!Type:Bank",
            "D01/15/2023",
            "T100.00",
            "N1234",
            "PGrocery Store",
            "MWeekly shopping",
            "LGroceries",
            "C*",
            "^",
            "D01/20/2023",
            "T-50.00",
            "N5678",
            "PGas Station",
            "MFuel",
            "LAuto:Fuel",
            "^"
        ]
        
        expected_content = "\n".join(expected_lines)
        self.assertEqual(qif_content, expected_content)
    
    def test_convert_bank_transactions_with_different_account_types(self):
        """Test converting bank transactions with different account types."""
        for account_type in [QIFAccountType.BANK, QIFAccountType.CASH, QIFAccountType.CCARD, QIFAccountType.ASSET, QIFAccountType.LIABILITY]:
            with self.subTest(account_type=account_type):
                qif_content = self.converter.convert_bank_transactions(self.bank_transactions, account_type)
                
                expected_lines = [
                    f"!Type:{account_type.value}",
                    "D01/15/2023",
                    "T100.00",
                    "N1234",
                    "PGrocery Store",
                    "MWeekly shopping",
                    "LGroceries",
                    "C*",
                    "^",
                    "D01/20/2023",
                    "T-50.00",
                    "N5678",
                    "PGas Station",
                    "MFuel",
                    "LAuto:Fuel",
                    "^"
                ]
                
                expected_content = "\n".join(expected_lines)
                self.assertEqual(qif_content, expected_content)
    
    def test_convert_investment_transactions(self):
        """Test converting investment transactions to QIF format."""
        qif_content = self.converter.convert_investment_transactions(self.investment_transactions)
        
        expected_lines = [
            "!Type:Invst",
            "D01/15/2023",
            "NBuy",
            "YAAPL",
            "I150.00",
            "Q10.00",
            "T1500.00",
            "O10.00",
            "PBuy Apple Inc.",
            "MPurchase",
            "LInvestments",
            "LBrokerage",
            "C*",
            "^",
            "D01/20/2023",
            "NSell",
            "YAAPL",
            "I160.00",
            "Q5.00",
            "T800.00",
            "O5.00",
            "PSell Apple Inc.",
            "MSale",
            "LInvestments",
            "LBrokerage",
            "^"
        ]
        
        expected_content = "\n".join(expected_lines)
        self.assertEqual(qif_content, expected_content)
    
    def test_convert_generic(self):
        """Test converting generic CSV data to QIF format."""
        rows = [
            {
                "Date": "2023-01-15",
                "Amount": "100.00",
                "Description": "Grocery Store",
                "Reference": "1234",
                "Memo": "Weekly shopping",
                "Category": "Groceries"
            },
            {
                "Date": "2023-01-20",
                "Amount": "-50.00",
                "Description": "Gas Station",
                "Reference": "5678",
                "Memo": "Fuel",
                "Category": "Auto:Fuel"
            }
        ]
        
        qif_content = self.converter.convert_generic(rows, QIFAccountType.BANK)
        
        expected_lines = [
            "!Type:Bank",
            "N1234",
            "PGrocery Store",
            "MWeekly shopping",
            "LGroceries",
            "D01/15/2023",
            "T100.00",
            "^",
            "N5678",
            "PGas Station",
            "MFuel",
            "LAuto:Fuel",
            "D01/20/2023",
            "T-50.00",
            "^"
        ]
        
        expected_content = "\n".join(expected_lines)
        self.assertEqual(qif_content, expected_content)
    
    def test_convert_generic_account(self):
        """Test converting generic CSV data to QIF account format."""
        rows = [
            {
                "Name": "Checking",
                "Type": "Bank",
                "Description": "Primary checking account",
                "Credit Limit": "0.00",
                "Statement Date": "2023-01-31",
                "Statement Balance": "1000.00"
            },
            {
                "Name": "Credit Card",
                "Type": "CCard",
                "Description": "Primary credit card",
                "Credit Limit": "5000.00",
                "Statement Date": "2023-01-15",
                "Statement Balance": "-500.00"
            }
        ]
        
        qif_content = self.converter.convert_generic(rows, QIFAccountType.ACCOUNT)
        
        expected_lines = [
            "!Type:Account",
            "NChecking",
            "TBank",
            "DPrimary checking account",
            "L0.00",
            "/2023-01-31",
            "$1000.00",
            "^",
            "NCredit Card",
            "TCCard",
            "DPrimary credit card",
            "L5000.00",
            "/2023-01-15",
            "$-500.00",
            "^"
        ]
        
        expected_content = "\n".join(expected_lines)
        self.assertEqual(qif_content, expected_content)
    
    def test_convert_generic_category(self):
        """Test converting generic CSV data to QIF category format."""
        rows = [
            {
                "Name": "Groceries",
                "Description": "Food and household items",
                "Tax Related": "No",
                "Income": "No",
                "Expense": "Yes",
                "Budget Amount": "500.00",
                "Tax Schedule": "A"
            },
            {
                "Name": "Salary",
                "Description": "Employment income",
                "Tax Related": "Yes",
                "Income": "Yes",
                "Expense": "No",
                "Budget Amount": "5000.00",
                "Tax Schedule": "B"
            }
        ]
        
        qif_content = self.converter.convert_generic(rows, QIFAccountType.CATEGORY)
        
        expected_lines = [
            "!Type:Cat",
            "NGroceries",
            "DFood and household items",
            "E",
            "B500.00",
            "RA",
            "^",
            "NSalary",
            "DEmployment income",
            "T",
            "I",
            "B5000.00",
            "RB",
            "^"
        ]
        
        expected_content = "\n".join(expected_lines)
        self.assertEqual(qif_content, expected_content)
    
    def test_convert_generic_class(self):
        """Test converting generic CSV data to QIF class format."""
        rows = [
            {
                "Name": "Personal",
                "Description": "Personal expenses"
            },
            {
                "Name": "Business",
                "Description": "Business expenses"
            }
        ]
        
        qif_content = self.converter.convert_generic(rows, QIFAccountType.CLASS)
        
        expected_lines = [
            "!Type:Class",
            "NPersonal",
            "DPersonal expenses",
            "^",
            "NBusiness",
            "DBusiness expenses",
            "^"
        ]
        
        expected_content = "\n".join(expected_lines)
        self.assertEqual(qif_content, expected_content)
    
    def test_parse_cleared_status(self):
        """Test parsing cleared status."""
        self.assertEqual(self.converter._parse_cleared_status("*"), "*")
        self.assertEqual(self.converter._parse_cleared_status("c"), "*")
        self.assertEqual(self.converter._parse_cleared_status("cleared"), "*")
        self.assertEqual(self.converter._parse_cleared_status("Cleared"), "*")
        
        self.assertEqual(self.converter._parse_cleared_status("x"), "X")
        self.assertEqual(self.converter._parse_cleared_status("r"), "X")
        self.assertEqual(self.converter._parse_cleared_status("reconciled"), "X")
        self.assertEqual(self.converter._parse_cleared_status("Reconciled"), "X")
        
        self.assertEqual(self.converter._parse_cleared_status(""), "")
        self.assertEqual(self.converter._parse_cleared_status("pending"), "")
        self.assertEqual(self.converter._parse_cleared_status(None), "")
    
    @patch('src.quickenqifimport.parsers.csv_parser.CSVParser')
    def test_convert_file_bank(self, mock_parser_class):
        """Test converting a bank CSV file to QIF."""
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_bank_transactions.return_value = self.bank_transactions
        
        self.converter.convert_file(self.bank_csv_path, self.qif_output_path, QIFAccountType.BANK)
        
        mock_parser_class.assert_called_once_with(date_format="%Y-%m-%d")
        mock_parser.parse_bank_transactions.assert_called_once_with(self.bank_csv_path, None)
        
        with open(self.qif_output_path, 'r') as file:
            qif_content = file.read()
        
        expected_lines = [
            "!Type:Bank",
            "D01/15/2023",
            "T100.00",
            "N1234",
            "PGrocery Store",
            "MWeekly shopping",
            "LGroceries",
            "C*",
            "^",
            "D01/20/2023",
            "T-50.00",
            "N5678",
            "PGas Station",
            "MFuel",
            "LAuto:Fuel",
            "^"
        ]
        
        expected_content = "\n".join(expected_lines)
        self.assertEqual(qif_content, expected_content)
    
    @patch('src.quickenqifimport.parsers.csv_parser.CSVParser')
    def test_convert_file_investment(self, mock_parser_class):
        """Test converting an investment CSV file to QIF."""
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_investment_transactions.return_value = self.investment_transactions
        
        self.converter.convert_file(self.investment_csv_path, self.qif_output_path, QIFAccountType.INVESTMENT)
        
        mock_parser_class.assert_called_once_with(date_format="%Y-%m-%d")
        mock_parser.parse_investment_transactions.assert_called_once_with(self.investment_csv_path, None)
        
        with open(self.qif_output_path, 'r') as file:
            qif_content = file.read()
        
        expected_lines = [
            "!Type:Invst",
            "D01/15/2023",
            "NBuy",
            "YAAPL",
            "I150.00",
            "Q10.00",
            "T1500.00",
            "O10.00",
            "PBuy Apple Inc.",
            "MPurchase",
            "LInvestments",
            "LBrokerage",
            "C*",
            "^",
            "D01/20/2023",
            "NSell",
            "YAAPL",
            "I160.00",
            "Q5.00",
            "T800.00",
            "O5.00",
            "PSell Apple Inc.",
            "MSale",
            "LInvestments",
            "LBrokerage",
            "^"
        ]
        
        expected_content = "\n".join(expected_lines)
        self.assertEqual(qif_content, expected_content)
    
    @patch('src.quickenqifimport.parsers.csv_parser.CSVParser')
    def test_convert_file_generic(self, mock_parser_class):
        """Test converting a generic CSV file to QIF."""
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        
        rows = [
            {
                "Name": "Personal",
                "Description": "Personal expenses"
            },
            {
                "Name": "Business",
                "Description": "Business expenses"
            }
        ]
        
        mock_parser.parse_file.return_value = rows
        
        self.converter.convert_file(self.bank_csv_path, self.qif_output_path, QIFAccountType.CLASS)
        
        mock_parser_class.assert_called_once_with(date_format="%Y-%m-%d")
        mock_parser.parse_file.assert_called_once_with(self.bank_csv_path, None)
        
        with open(self.qif_output_path, 'r') as file:
            qif_content = file.read()
        
        expected_lines = [
            "!Type:Class",
            "NPersonal",
            "DPersonal expenses",
            "^",
            "NBusiness",
            "DBusiness expenses",
            "^"
        ]
        
        expected_content = "\n".join(expected_lines)
        self.assertEqual(qif_content, expected_content)
    
    @patch('src.quickenqifimport.parsers.csv_parser.CSVParser')
    def test_convert_file_with_template(self, mock_parser_class):
        """Test converting a CSV file to QIF with a template."""
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_bank_transactions.return_value = self.bank_transactions
        
        self.converter.convert_file(self.bank_csv_path, self.qif_output_path, QIFAccountType.BANK, self.bank_template)
        
        mock_parser_class.assert_called_once_with(date_format="%Y-%m-%d")
        mock_parser.parse_bank_transactions.assert_called_once_with(self.bank_csv_path, self.bank_template)


if __name__ == "__main__":
    unittest.main()
