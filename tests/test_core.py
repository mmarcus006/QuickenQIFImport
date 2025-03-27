import unittest
from datetime import datetime
import os
import tempfile
import shutil

from src.quickenqifimport.models.qif_models import QIFAccountType
from src.quickenqifimport.models.csv_models import CSVTemplate
from src.quickenqifimport.core.converter import Converter
from src.quickenqifimport.core.template_manager import TemplateManager
from src.quickenqifimport.core.app import App


class TestConverter(unittest.TestCase):
    """Test cases for the Converter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.converter = Converter()
        
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
        
        self.bank_csv_content = """Date,Amount,Description,Reference,Memo,Category,Account,Status
2023-01-15,100.00,Grocery Store,1234,Weekly shopping,Groceries,Checking,*
2023-01-20,-50.00,Gas Station,,Fuel purchase,Auto:Fuel,Checking,
"""
        
        self.temp_dir = tempfile.mkdtemp()
        self.qif_file_path = os.path.join(self.temp_dir, "test.qif")
        self.csv_file_path = os.path.join(self.temp_dir, "test.csv")
        
        with open(self.qif_file_path, 'w') as file:
            file.write(self.bank_qif_content)
            
        with open(self.csv_file_path, 'w') as file:
            file.write(self.bank_csv_content)
    
    def tearDown(self):
        """Tear down test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_convert_qif_to_csv(self):
        """Test converting QIF to CSV."""
        output_path = os.path.join(self.temp_dir, "output.csv")
        
        self.converter.convert_qif_to_csv(self.qif_file_path, output_path)
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as file:
            content = file.read()
            self.assertIn("Date,Amount,Description,Reference,Memo,Category,Status", content)
            self.assertIn("2023-01-15,100.0,Grocery Store,1234,Weekly shopping,Groceries,", content)
            self.assertIn("2023-01-20,-50.0,Gas Station,,,Auto:Fuel,", content)
    
    def test_convert_csv_to_qif(self):
        """Test converting CSV to QIF."""
        output_path = os.path.join(self.temp_dir, "output.qif")
        
        self.converter.convert_csv_to_qif(self.csv_file_path, output_path, QIFAccountType.BANK)
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as file:
            content = file.read()
            self.assertIn("!Type:Bank", content)
            self.assertIn("D01/15/2023", content)
            self.assertIn("T100.00", content)
            self.assertIn("PGrocery Store", content)
    
    def test_detect_file_type(self):
        """Test file type detection."""
        self.assertEqual(self.converter.detect_file_type(self.qif_file_path), "qif")
        
        self.assertEqual(self.converter.detect_file_type(self.csv_file_path), "csv")
        
        unknown_file_path = os.path.join(self.temp_dir, "unknown.txt")
        with open(unknown_file_path, 'w') as file:
            file.write("This is not a QIF or CSV file.")
            
        self.assertEqual(self.converter.detect_file_type(unknown_file_path), "unknown")
        
        with self.assertRaises(FileNotFoundError):
            self.converter.detect_file_type(os.path.join(self.temp_dir, "nonexistent.qif"))
    
    def test_detect_qif_account_type(self):
        """Test QIF account type detection."""
        self.assertEqual(self.converter.detect_qif_account_type(self.qif_file_path), QIFAccountType.BANK)
        
        for account_type in [QIFAccountType.CASH, QIFAccountType.CCARD, QIFAccountType.INVESTMENT]:
            file_path = os.path.join(self.temp_dir, f"{account_type.value}.qif")
            with open(file_path, 'w') as file:
                file.write(f"!Type:{account_type.value}\nD01/15/2023\nT100.00\n^")
                
            self.assertEqual(self.converter.detect_qif_account_type(file_path), account_type)
    
    def test_detect_csv_template_type(self):
        """Test CSV template type detection."""
        self.assertEqual(self.converter.detect_csv_template_type(self.csv_file_path), "bank")
        
        investment_csv_path = os.path.join(self.temp_dir, "investment.csv")
        with open(investment_csv_path, 'w') as file:
            file.write("Date,Action,Security,Quantity,Price,Amount,Commission\n")
            file.write("2023-01-15,Buy,AAPL,10,150.00,1500.00,7.99\n")
            
        self.assertEqual(self.converter.detect_csv_template_type(investment_csv_path), "investment")
    
    def test_preview_qif_file(self):
        """Test QIF file preview."""
        preview = self.converter.preview_qif_file(self.qif_file_path)
        
        self.assertEqual(preview["account_type"], "Bank")
        self.assertEqual(len(preview["transactions"]), 2)
        self.assertEqual(preview["transactions"][0]["payee"], "Grocery Store")
        self.assertEqual(preview["transactions"][1]["payee"], "Gas Station")
    
    def test_preview_csv_file(self):
        """Test CSV file preview."""
        preview = self.converter.preview_csv_file(self.csv_file_path)
        
        self.assertEqual(preview["delimiter"], ",")
        self.assertIn("Date", preview["headers"])
        self.assertIn("Amount", preview["headers"])
        self.assertEqual(len(preview["rows"]), 2)
        self.assertEqual(preview["rows"][0]["Description"], "Grocery Store")
        self.assertEqual(preview["rows"][1]["Description"], "Gas Station")


class TestTemplateManager(unittest.TestCase):
    """Test cases for the TemplateManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_manager = TemplateManager(self.temp_dir)
    
    def tearDown(self):
        """Tear down test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_create_template(self):
        """Test template creation."""
        field_mapping = {
            "Date": "date",
            "Amount": "amount",
            "Description": "payee"
        }
        
        template = self.template_manager.create_template(
            name="Test",
            account_type="Bank",
            field_mapping=field_mapping,
            description="Test template",
            date_format="%Y-%m-%d",
            delimiter=","
        )
        
        self.assertEqual(template.name, "Test")
        self.assertEqual(template.account_type, "Bank")
        self.assertEqual(template.field_mapping, field_mapping)
        self.assertEqual(template.description, "Test template")
        self.assertEqual(template.date_format, "%Y-%m-%d")
        self.assertEqual(template.delimiter, ",")
        
        with self.assertRaises(ValueError):
            self.template_manager.create_template(
                name="",
                account_type="Bank",
                field_mapping=field_mapping
            )
    
    def test_save_and_load_template(self):
        """Test saving and loading templates."""
        field_mapping = {
            "Date": "date",
            "Amount": "amount",
            "Description": "payee"
        }
        
        template = self.template_manager.create_template(
            name="Test",
            account_type="Bank",
            field_mapping=field_mapping
        )
        
        file_path = self.template_manager.save_template(template)
        
        self.assertTrue(os.path.exists(file_path))
        
        loaded_template = self.template_manager.load_template(file_path)
        
        self.assertEqual(loaded_template.name, template.name)
        self.assertEqual(loaded_template.account_type, template.account_type)
        self.assertEqual(loaded_template.field_mapping, template.field_mapping)
    
    def test_list_templates(self):
        """Test template listing."""
        for i in range(3):
            template = self.template_manager.create_template(
                name=f"Template{i}",
                account_type="Bank",
                field_mapping={"Date": "date"}
            )
            self.template_manager.save_template(template)
            
        templates = self.template_manager.list_templates()
        
        self.assertEqual(len(templates), 3)
        for i in range(3):
            self.assertIn(f"Template{i}.json", templates)
    
    def test_get_template_path(self):
        """Test getting template path."""
        template = self.template_manager.create_template(
            name="Test",
            account_type="Bank",
            field_mapping={"Date": "date"}
        )
        self.template_manager.save_template(template)
        
        path = self.template_manager.get_template_path("Test")
        
        self.assertTrue(os.path.exists(path))
        self.assertEqual(os.path.basename(path), "Test.json")
        
        with self.assertRaises(FileNotFoundError):
            self.template_manager.get_template_path("NonExistent")
    
    def test_delete_template(self):
        """Test template deletion."""
        template = self.template_manager.create_template(
            name="Test",
            account_type="Bank",
            field_mapping={"Date": "date"}
        )
        self.template_manager.save_template(template)
        
        path = self.template_manager.get_template_path("Test")
        self.assertTrue(os.path.exists(path))
        
        self.template_manager.delete_template("Test")
        
        self.assertFalse(os.path.exists(path))
        
        with self.assertRaises(FileNotFoundError):
            self.template_manager.delete_template("NonExistent")
    
    def test_create_default_templates(self):
        """Test creating default templates."""
        templates = self.template_manager.create_default_templates()
        
        self.assertEqual(len(templates), 3)
        
        for path in templates:
            self.assertTrue(os.path.exists(path))
            
        template_list = self.template_manager.list_templates()
        self.assertEqual(len(template_list), 3)
        self.assertIn("Bank.json", template_list)
        self.assertIn("Credit Card.json", template_list)
        self.assertIn("Investment.json", template_list)


class TestApp(unittest.TestCase):
    """Test cases for the App class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.app = App(templates_dir=self.temp_dir)
        
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
        
        self.bank_csv_content = """Date,Amount,Description,Reference,Memo,Category,Account,Status
2023-01-15,100.00,Grocery Store,1234,Weekly shopping,Groceries,Checking,*
2023-01-20,-50.00,Gas Station,,Fuel purchase,Auto:Fuel,Checking,
"""
        
        self.qif_file_path = os.path.join(self.temp_dir, "test.qif")
        self.csv_file_path = os.path.join(self.temp_dir, "test.csv")
        
        with open(self.qif_file_path, 'w') as file:
            file.write(self.bank_qif_content)
            
        with open(self.csv_file_path, 'w') as file:
            file.write(self.bank_csv_content)
    
    def tearDown(self):
        """Tear down test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_convert_qif_to_csv(self):
        """Test converting QIF to CSV."""
        output_path = os.path.join(self.temp_dir, "output.csv")
        
        self.app.convert_qif_to_csv(self.qif_file_path, output_path)
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as file:
            content = file.read()
            self.assertIn("Date,Amount,Description,Reference,Memo,Category,Status", content)
            self.assertIn("2023-01-15,100.0,Grocery Store,1234,Weekly shopping,Groceries,", content)
            self.assertIn("2023-01-20,-50.0,Gas Station,,,Auto:Fuel,", content)
    
    def test_convert_csv_to_qif(self):
        """Test converting CSV to QIF."""
        output_path = os.path.join(self.temp_dir, "output.qif")
        
        self.app.convert_csv_to_qif(self.csv_file_path, output_path, QIFAccountType.BANK)
        
        self.assertTrue(os.path.exists(output_path))
        
        with open(output_path, 'r') as file:
            content = file.read()
            self.assertIn("!Type:Bank", content)
            self.assertIn("D01/15/2023", content)
            self.assertIn("T100.00", content)
            self.assertIn("PGrocery Store", content)
    
    def test_create_template(self):
        """Test template creation."""
        field_mapping = {
            "Date": "date",
            "Amount": "amount",
            "Description": "payee"
        }
        
        template = self.app.create_template(
            name="Test",
            account_type="Bank",
            field_mapping=field_mapping,
            description="Test template",
            date_format="%Y-%m-%d",
            delimiter=",",
            save=True
        )
        
        self.assertEqual(template.name, "Test")
        self.assertEqual(template.account_type, "Bank")
        self.assertEqual(template.field_mapping, field_mapping)
        self.assertEqual(template.description, "Test template")
        self.assertEqual(template.date_format, "%Y-%m-%d")
        self.assertEqual(template.delimiter, ",")
        
        template_path = os.path.join(self.temp_dir, "Test.json")
        self.assertTrue(os.path.exists(template_path))
    
    def test_create_default_templates(self):
        """Test creating default templates."""
        templates = self.app.create_default_templates()
        
        self.assertEqual(len(templates), 3)
        
        for path in templates:
            self.assertTrue(os.path.exists(path))
            
        template_list = self.app.template_manager.list_templates()
        self.assertEqual(len(template_list), 3)
        self.assertIn("Bank.json", template_list)
        self.assertIn("Credit Card.json", template_list)
        self.assertIn("Investment.json", template_list)


if __name__ == "__main__":
    unittest.main()
